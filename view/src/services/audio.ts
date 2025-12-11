/**
 * Audio API service
 * Handles audio analysis and WebSocket streaming
 * Maps to FastAPI endpoints in api/websocket_audio_router.py
 */

import { postFormData } from './api';

const WS_URL = import.meta.env.VITE_API_URL?.replace('http', 'ws') || 'ws://localhost:8000';

export interface AudioAnalysisResult {
  transcript: string;
  detected_language: string;
  language_confidence: number;
  translated_text?: string;
  classification: {
    incident_type: string;
    severity: string;
    suggested_unit: string;
    incident_confidence: number;
    severity_confidence: number;
    dispatch_confidence: number;
  };
}

export interface PartialResult {
  type: 'partial';
  segment_index: number;
  timestamp: string;
  partial_transcript: string;
  detected_language: string;
  partial_translated_text?: string;
  translated_language?: string;
  classification: {
    incident_type: string;
    severity: string;
    suggested_unit: string;
    incident_confidence: number;
    severity_confidence: number;
    dispatch_confidence: number;
  };
}

export interface FinalResult {
  type: 'final';
  timestamp: string;
  session_duration_seconds: number;
  total_segments: number;
  original_transcript: string;
  detected_language: string;
  translated_text?: string;
  translated_language?: string;
  classification: {
    incident_type: string;
    severity: string;
    suggested_unit: string;
    incident_confidence: number;
    severity_confidence: number;
    dispatch_confidence: number;
  };
}

export interface WebSocketMessage {
  type: 'partial' | 'final' | 'error' | 'session_started';
  [key: string]: unknown;
}

export interface WebSocketOptions {
  translate?: boolean;
  targetLanguage?: string;
  onPartial?: (result: PartialResult) => void;
  onFinal?: (result: FinalResult) => void;
  onError?: (error: { error: string; details?: string }) => void;
  onSessionStarted?: () => void;
  onClose?: () => void;
  onOpen?: () => void;
}

/**
 * Analyze audio file via REST API
 * @param file Audio file to analyze
 */
export async function analyzeAudio(file: File): Promise<AudioAnalysisResult> {
  const formData = new FormData();
  formData.append('audio', file);
  return postFormData<AudioAnalysisResult>('/api/audio/analyze', formData);
}

/**
 * Create a WebSocket connection for real-time audio streaming
 * @param options WebSocket configuration and callbacks
 * @returns WebSocket controller with send and close methods
 */
export function createAudioWebSocket(options: WebSocketOptions = {}) {
  const {
    translate = true,
    targetLanguage = 'ar',
    onPartial,
    onFinal,
    onError,
    onSessionStarted,
    onClose,
    onOpen,
  } = options;

  const wsUrl = `${WS_URL}/ws/live-audio-stream?translate=${translate}&target_language=${targetLanguage}`;
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    onOpen?.();
  };

  ws.onmessage = (event) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      switch (message.type) {
        case 'session_started':
          onSessionStarted?.();
          break;
        case 'partial':
          onPartial?.(message as unknown as PartialResult);
          break;
        case 'final':
          onFinal?.(message as unknown as FinalResult);
          break;
        case 'error':
          onError?.({
            error: message.error as string,
            details: message.details as string | undefined,
          });
          break;
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    onError?.({ error: 'WebSocket connection error' });
  };

  ws.onclose = () => {
    onClose?.();
  };

  return {
    /**
     * Send binary PCM audio data
     * @param audioData ArrayBuffer or Blob of PCM audio data
     */
    sendAudio: (audioData: ArrayBuffer | Blob) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(audioData);
      }
    },

    /**
     * Send a control message to configure the session
     */
    sendControl: (translateEnabled: boolean, language: string) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'control',
          translate: translateEnabled,
          target_language: language,
        }));
      }
    },

    /**
     * Close the WebSocket connection
     */
    close: () => {
      ws.close();
    },

    /**
     * Get current connection state
     */
    getReadyState: () => ws.readyState,

    /**
     * Check if connected
     */
    isConnected: () => ws.readyState === WebSocket.OPEN,
  };
}

/**
 * Get WebSocket endpoint information
 */
export async function getWebSocketInfo(): Promise<{
  websocket_endpoint: string;
  pcm_audio_format: Record<string, string>;
  session_parameters: Record<string, unknown>;
  message_types: Record<string, unknown>;
  usage_example: Record<string, unknown>;
}> {
  const response = await fetch(`${WS_URL.replace('ws', 'http')}/ws/info`);
  return response.json();
}

export const audioService = {
  analyzeAudio,
  createAudioWebSocket,
  getWebSocketInfo,
};

export default audioService;
