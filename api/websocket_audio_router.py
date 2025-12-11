"""WebSocket Audio Streaming Router

Provides real-time PCM audio streaming endpoint with continuous partial results.
Follows MVC architecture pattern with thin router delegating to service layer.
"""

import logging
import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket Audio Streaming"])

# Global service instance (initialized in main.py)
_websocket_audio_service = None
_incident_classifier = None
_severity_classifier = None
_dispatch_classifier = None


def get_websocket_audio_service():
    """Get WebSocket audio service instance."""
    if _websocket_audio_service is None:
        raise RuntimeError("WebSocket audio service not initialized")
    return _websocket_audio_service


def get_classifiers():
    """Get classifier instances."""
    if _incident_classifier is None or _severity_classifier is None or _dispatch_classifier is None:
        raise RuntimeError("Classifiers not initialized")
    return _incident_classifier, _severity_classifier, _dispatch_classifier


@router.get("/info")
async def websocket_info():
    """Get WebSocket endpoint information and PCM audio format requirements.

    Returns:
        JSON with WebSocket endpoint details and audio format specifications
    """
    return JSONResponse(content={
        "websocket_endpoint": "/ws/live-audio-stream",
        "description": "Real-time PCM audio streaming with continuous partial results",
        "pcm_audio_format": {
            "encoding": "Linear PCM",
            "bit_depth": "16-bit signed",
            "channels": "Mono (1 channel)",
            "sample_rate": "16000 Hz (recommended)",
            "frame_duration": "10-100 ms recommended",
            "byte_order": "Little-endian"
        },
        "session_parameters": {
            "translate": {
                "type": "boolean",
                "default": True,
                "description": "Enable translation of transcripts"
            },
            "target_language": {
                "type": "string",
                "default": "ar",
                "description": "Target language code for translation (e.g., 'ar', 'en', 'es')"
            }
        },
        "message_types": {
            "incoming": {
                "control": {
                    "description": "Initial control message to set session parameters",
                    "example": {
                        "type": "control",
                        "translate": True,
                        "target_language": "ar"
                    }
                },
                "audio": {
                    "description": "Binary PCM audio frames",
                    "format": "Raw bytes (16-bit PCM mono)"
                }
            },
            "outgoing": {
                "partial": {
                    "description": "Partial transcription and classification results",
                    "fields": [
                        "type",
                        "segment_index",
                        "timestamp",
                        "partial_transcript",
                        "detected_language",
                        "partial_translated_text (if translate=true)",
                        "translated_language (if translate=true)",
                        "classification"
                    ]
                },
                "final": {
                    "description": "Final summary with complete transcription and classification",
                    "fields": [
                        "type",
                        "timestamp",
                        "session_duration_seconds",
                        "total_segments",
                        "original_transcript",
                        "detected_language",
                        "translated_text (if translate=true)",
                        "translated_language (if translate=true)",
                        "classification"
                    ]
                },
                "error": {
                    "description": "Error message",
                    "fields": ["type", "error", "details"]
                }
            }
        },
        "usage_example": {
            "connect": "ws://localhost:8000/ws/live-audio-stream?translate=true&target_language=ar",
            "alternative": "Send control message after connection",
            "workflow": [
                "1. Connect to WebSocket endpoint",
                "2. Send control message OR use query params for session config",
                "3. Stream PCM audio frames as binary messages",
                "4. Receive partial JSON results during streaming",
                "5. Receive final JSON summary when done",
                "6. Close connection"
            ]
        }
    })


@router.websocket("/live-audio-stream")
async def websocket_audio_stream(
    websocket: WebSocket,
    translate: Optional[bool] = Query(default=True, description="Enable translation"),
    target_language: Optional[str] = Query(default="ar", description="Target language code")
):
    """WebSocket endpoint for real-time PCM audio streaming with continuous analysis.

    This endpoint:
    - Receives raw PCM audio frames (16-bit signed, mono, 16kHz)
    - Buffers and processes audio chunks with Faster-Whisper
    - Optionally translates transcripts with GPT-4o-mini
    - Streams partial classification results
    - Sends final summary on session end

    Session Configuration:
        - Can be set via query params (translate, target_language)
        - Or via initial JSON control message

    Message Flow:
        Client -> Server: Binary PCM audio frames OR JSON control message
        Server -> Client: JSON partial results + final summary

    Args:
        websocket: WebSocket connection
        translate: Enable translation (default: True)
        target_language: Target language for translation (default: "ar")
    """
    await websocket.accept()

    service = get_websocket_audio_service()
    incident_classifier, severity_classifier, dispatch_classifier = get_classifiers()

    # Initialize session state with default or query params
    session_state = None
    session_configured = False

    logger.info(f"WebSocket connection accepted: translate={translate}, target_language={target_language}")

    try:
        async for message in websocket.iter_bytes():
            try:
                # Check if this is a JSON control message (first message)
                if not session_configured:
                    try:
                        # Try to parse as JSON control message
                        control_data = json.loads(message.decode('utf-8'))

                        if control_data.get("type") == "control":
                            # Use control message parameters
                            translate = control_data.get("translate", True)
                            target_language = control_data.get("target_language", "ar")
                            logger.info(f"Session configured via control message: translate={translate}, target_language={target_language}")

                            # Create session state
                            session_state = service.create_session_state(
                                translate=translate,
                                target_language=target_language
                            )
                            session_configured = True

                            # Send acknowledgment
                            await websocket.send_json({
                                "type": "session_started",
                                "translate": translate,
                                "target_language": target_language,
                                "message": "Session configured successfully"
                            })
                            continue

                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Not a JSON message, treat as audio data
                        pass

                # If session not yet configured, use query params
                if not session_configured:
                    session_state = service.create_session_state(
                        translate=translate,
                        target_language=target_language
                    )
                    session_configured = True
                    logger.info(f"Session configured via query params: translate={translate}, target_language={target_language}")

                # Process binary PCM audio data
                if isinstance(message, bytes):
                    # Add PCM frames to buffer
                    session_state["audio_buffer"].extend(message)

                    logger.debug(f"Received {len(message)} bytes, buffer size: {len(session_state['audio_buffer'])} bytes")

                    # Check if buffer is large enough to process
                    if len(session_state["audio_buffer"]) >= service.min_chunk_size_bytes:
                        # Process chunk and get partial result
                        partial_result = service.process_audio_chunk(
                            session_state=session_state,
                            incident_classifier=incident_classifier,
                            severity_classifier=severity_classifier,
                            dispatch_classifier=dispatch_classifier
                        )

                        # Send partial result if available
                        if partial_result:
                            await websocket.send_json(partial_result)
                            logger.info(f"Sent partial result: segment {partial_result.get('segment_index')}")

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "error": str(e),
                    "details": "Error processing audio data"
                })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected by client")

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e),
                "details": "Unexpected error in WebSocket connection"
            })
        except:
            pass

    finally:
        # Generate and send final result
        if session_state is not None:
            try:
                logger.info("Generating final result...")
                # final_result = service.generate_final_result(...)
                final_result = service.generate_final_result(
                    session_state=session_state,
                    incident_classifier=incident_classifier,
                    severity_classifier=severity_classifier,
                    dispatch_classifier=dispatch_classifier
                )
                
                # Check if websocket is still connected before sending
                if websocket.client_state.name == "CONNECTED":
                    await websocket.send_json(final_result)
                    logger.info("Final result sent successfully")

            except Exception as e:
                logger.error(f"Error sending final result: {e}", exc_info=True)

        # Close connection
        try:
            await websocket.close()
            logger.info("WebSocket connection closed")
        except:
            pass


# Initialization functions (called from main.py)
def init_websocket_audio_service(service, incident_clf, severity_clf, dispatch_clf):
    """Initialize WebSocket audio service and classifiers.

    Args:
        service: WebSocketAudioService instance
        incident_clf: IncidentClassifier instance
        severity_clf: SeverityClassifier instance
        dispatch_clf: DispatchClassifier instance
    """
    global _websocket_audio_service, _incident_classifier, _severity_classifier, _dispatch_classifier

    _websocket_audio_service = service
    _incident_classifier = incident_clf
    _severity_classifier = severity_clf
    _dispatch_classifier = dispatch_clf

    logger.info("WebSocket audio router initialized with service and classifiers")
