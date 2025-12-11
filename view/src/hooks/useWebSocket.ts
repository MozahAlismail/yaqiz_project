import { useState, useRef, useCallback, useEffect } from 'react';

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export interface UseWebSocketOptions {
  /** Whether to connect automatically on mount */
  autoConnect?: boolean;
  /** Whether to reconnect automatically on disconnect */
  autoReconnect?: boolean;
  /** Delay between reconnection attempts in milliseconds */
  reconnectDelay?: number;
  /** Maximum number of reconnection attempts */
  maxReconnectAttempts?: number;
  /** Callback when connection opens */
  onOpen?: () => void;
  /** Callback when message is received */
  onMessage?: (data: unknown) => void;
  /** Callback when connection closes */
  onClose?: (event: CloseEvent) => void;
  /** Callback when error occurs */
  onError?: (error: Event) => void;
}

export interface UseWebSocketReturn {
  /** Current connection status */
  status: WebSocketStatus;
  /** Send a message (string or object) */
  send: (data: string | object) => void;
  /** Send binary data */
  sendBinary: (data: ArrayBuffer | Blob) => void;
  /** Connect to the WebSocket server */
  connect: () => void;
  /** Disconnect from the WebSocket server */
  disconnect: () => void;
  /** Last received message */
  lastMessage: unknown;
  /** Number of reconnection attempts */
  reconnectCount: number;
}

/**
 * Hook for managing WebSocket connections
 * @param url WebSocket URL
 * @param options Configuration options
 */
export function useWebSocket(
  url: string,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const {
    autoConnect = true,
    autoReconnect = true,
    reconnectDelay = 3000,
    maxReconnectAttempts = 5,
    onOpen,
    onMessage,
    onClose,
    onError,
  } = options;

  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<unknown>(null);
  const [reconnectCount, setReconnectCount] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const mountedRef = useRef(true);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus('connecting');

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (mountedRef.current) {
          setStatus('connected');
          setReconnectCount(0);
          onOpen?.();
        }
      };

      ws.onmessage = (event) => {
        if (mountedRef.current) {
          let data: unknown = event.data;

          // Try to parse JSON messages
          if (typeof event.data === 'string') {
            try {
              data = JSON.parse(event.data);
            } catch {
              // Keep as string if not JSON
            }
          }

          setLastMessage(data);
          onMessage?.(data);
        }
      };

      ws.onclose = (event) => {
        if (mountedRef.current) {
          setStatus('disconnected');
          onClose?.(event);

          // Attempt reconnection if enabled
          if (
            autoReconnect &&
            reconnectCount < maxReconnectAttempts &&
            !event.wasClean
          ) {
            reconnectTimeoutRef.current = setTimeout(() => {
              if (mountedRef.current) {
                setReconnectCount((prev) => prev + 1);
                connect();
              }
            }, reconnectDelay);
          }
        }
      };

      ws.onerror = (error) => {
        if (mountedRef.current) {
          setStatus('error');
          onError?.(error);
        }
      };
    } catch (error) {
      setStatus('error');
      console.error('WebSocket connection error:', error);
    }
  }, [
    url,
    autoReconnect,
    reconnectDelay,
    maxReconnectAttempts,
    reconnectCount,
    onOpen,
    onMessage,
    onClose,
    onError,
  ]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setStatus('disconnected');
    setReconnectCount(0);
  }, []);

  const send = useCallback((data: string | object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      wsRef.current.send(message);
    } else {
      console.warn('WebSocket is not connected. Cannot send message.');
    }
  }, []);

  const sendBinary = useCallback((data: ArrayBuffer | Blob) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(data);
    } else {
      console.warn('WebSocket is not connected. Cannot send binary data.');
    }
  }, []);

  // Connect on mount if autoConnect is enabled
  useEffect(() => {
    mountedRef.current = true;

    if (autoConnect) {
      connect();
    }

    return () => {
      mountedRef.current = false;
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    status,
    send,
    sendBinary,
    connect,
    disconnect,
    lastMessage,
    reconnectCount,
  };
}

export default useWebSocket;
