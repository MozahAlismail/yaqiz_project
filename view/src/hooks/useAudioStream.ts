import { useState, useRef, useCallback, useEffect } from 'react';
import { useWebSocket, WebSocketStatus } from './useWebSocket';

export interface TranscriptionData {
  original_text: string;
  original_language: string;
  translated_text: string | null;
  translated_language: string | null;
  translation_enabled: boolean;
  text_used_for_classification: string;
  classification_language: string;
}

export interface ClassificationData {
  incident?: {
    incident_type: string;
    confidence: number;
    reasoning: string;
    keywords_found: string[];
  };
  severity?: {
    severity_level: string;
    confidence: number;
    reasoning: string;
    urgency_indicators: string[];
  };
  dispatch?: {
    dispatch_unit: string;
    confidence: number;
    reasoning: string;
    estimated_priority: string;
  };
}

export interface StreamingResponse {
  type: 'session_started' | 'partial' | 'final' | 'control_ack' | 'error';
  session_id?: string;
  segment_index?: number;
  timestamp?: string;
  transcription?: TranscriptionData;
  classification?: ClassificationData;
  // Legacy fields
  partial_transcript?: string;
  detected_language?: string;
  partial_translated_text?: string;
  translated_language?: string;
  error?: string;
}

export interface UseAudioStreamOptions {
  /** WebSocket URL (default: ws://localhost:8000/ws/live-audio-stream) */
  url?: string;
  /** Enable translation (default: false) */
  translate?: boolean;
  /** Target language for translation (default: ar) */
  targetLanguage?: string;
  /** Processing mode: 'direct' or 'streaming' (default: streaming) */
  mode?: 'direct' | 'streaming';
  /** Callback when transcription is updated */
  onTranscriptionUpdate?: (transcription: TranscriptionData) => void;
  /** Callback when classification is updated */
  onClassificationUpdate?: (classification: ClassificationData) => void;
  /** Callback when session starts */
  onSessionStart?: (sessionId: string) => void;
  /** Callback when session ends */
  onSessionEnd?: (response: StreamingResponse) => void;
  /** Callback on error */
  onError?: (error: string) => void;
}

export interface UseAudioStreamReturn {
  /** Current connection status */
  status: WebSocketStatus;
  /** Whether audio is currently streaming */
  isStreaming: boolean;
  /** Current session ID */
  sessionId: string | null;
  /** Current transcription data */
  transcription: TranscriptionData | null;
  /** Current classification data */
  classification: ClassificationData | null;
  /** Translation enabled state */
  translationEnabled: boolean;
  /** Start streaming audio */
  startStreaming: () => void;
  /** Stop streaming audio */
  stopStreaming: () => void;
  /** Send audio data (PCM bytes) */
  sendAudio: (data: ArrayBuffer) => void;
  /** Toggle translation on/off */
  setTranslation: (enabled: boolean, targetLanguage?: string) => void;
  /** Last error message */
  lastError: string | null;
}

const DEFAULT_URL = 'ws://localhost:8000/ws/live-audio-stream';

export function useAudioStream(options: UseAudioStreamOptions = {}): UseAudioStreamReturn {
  const {
    url = DEFAULT_URL,
    translate = false,
    targetLanguage = 'ar',
    mode = 'streaming',
    onTranscriptionUpdate,
    onClassificationUpdate,
    onSessionStart,
    onSessionEnd,
    onError,
  } = options;

  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [transcription, setTranscription] = useState<TranscriptionData | null>(null);
  const [classification, setClassification] = useState<ClassificationData | null>(null);
  const [translationEnabled, setTranslationEnabled] = useState(translate);
  const [currentTargetLanguage, setCurrentTargetLanguage] = useState(targetLanguage);
  const [lastError, setLastError] = useState<string | null>(null);

  const streamingRef = useRef(false);

  // Build WebSocket URL with query params
  const wsUrl = `${url}?translate=${translationEnabled}&target_language=${currentTargetLanguage}&mode=${mode}`;

  const handleMessage = useCallback((data: unknown) => {
    const response = data as StreamingResponse;

    switch (response.type) {
      case 'session_started':
        setSessionId(response.session_id || null);
        onSessionStart?.(response.session_id || '');
        break;

      case 'partial':
      case 'final':
        // Update transcription
        if (response.transcription) {
          setTranscription(response.transcription);
          onTranscriptionUpdate?.(response.transcription);
        } else if (response.partial_transcript) {
          // Legacy format fallback
          const legacyTranscription: TranscriptionData = {
            original_text: response.partial_transcript,
            original_language: response.detected_language || 'unknown',
            translated_text: response.partial_translated_text || null,
            translated_language: response.translated_language || null,
            translation_enabled: translationEnabled,
            text_used_for_classification: response.partial_translated_text || response.partial_transcript,
            classification_language: response.translated_language || response.detected_language || 'ar',
          };
          setTranscription(legacyTranscription);
          onTranscriptionUpdate?.(legacyTranscription);
        }

        // Update classification
        if (response.classification) {
          setClassification(response.classification);
          onClassificationUpdate?.(response.classification);
        }

        // Handle final response
        if (response.type === 'final') {
          onSessionEnd?.(response);
        }
        break;

      case 'control_ack':
        console.log('Translation setting acknowledged');
        break;

      case 'error':
        setLastError(response.error || 'Unknown error');
        onError?.(response.error || 'Unknown error');
        break;
    }
  }, [translationEnabled, onTranscriptionUpdate, onClassificationUpdate, onSessionStart, onSessionEnd, onError]);

  const { status, send, sendBinary, connect, disconnect } = useWebSocket(wsUrl, {
    autoConnect: false,
    autoReconnect: false,
    onMessage: handleMessage,
    onOpen: () => {
      console.log('Audio stream connected');
    },
    onClose: () => {
      setIsStreaming(false);
      streamingRef.current = false;
    },
    onError: (error) => {
      setLastError('WebSocket connection error');
      onError?.('WebSocket connection error');
    },
  });

  const startStreaming = useCallback(() => {
    if (!streamingRef.current) {
      setTranscription(null);
      setClassification(null);
      setLastError(null);
      setSessionId(null);
      connect();
      setIsStreaming(true);
      streamingRef.current = true;
    }
  }, [connect]);

  const stopStreaming = useCallback(() => {
    if (streamingRef.current) {
      disconnect();
      setIsStreaming(false);
      streamingRef.current = false;
    }
  }, [disconnect]);

  const sendAudio = useCallback((data: ArrayBuffer) => {
    if (streamingRef.current && status === 'connected') {
      sendBinary(data);
    }
  }, [status, sendBinary]);

  const setTranslation = useCallback((enabled: boolean, newTargetLanguage?: string) => {
    setTranslationEnabled(enabled);
    if (newTargetLanguage) {
      setCurrentTargetLanguage(newTargetLanguage);
    }

    // If connected, send control message to update settings
    if (status === 'connected') {
      send({
        type: 'control',
        translate: enabled,
        target_language: newTargetLanguage || currentTargetLanguage,
      });
    }
  }, [status, send, currentTargetLanguage]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (streamingRef.current) {
        disconnect();
      }
    };
  }, [disconnect]);

  return {
    status,
    isStreaming,
    sessionId,
    transcription,
    classification,
    translationEnabled,
    startStreaming,
    stopStreaming,
    sendAudio,
    setTranslation,
    lastError,
  };
}

export default useAudioStream;
