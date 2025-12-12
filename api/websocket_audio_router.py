"""WebSocket Audio Streaming Router

Provides real-time PCM audio streaming endpoint with continuous partial results.
Supports two modes:
- direct: Original mode - immediate classification without LangGraph
- streaming: New mode - LangGraph streaming workflow with confidence gate

Follows MVC architecture pattern with thin router delegating to service layer.
"""

import logging
import json
import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket Audio Streaming"])

# Global service instance (initialized in main.py)
_websocket_audio_service = None
_incident_classifier = None
_severity_classifier = None
_dispatch_classifier = None

# Streaming graph services (initialized in main.py)
_streaming_graph_service = None
_streaming_case_controller = None
_db_config = None


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


def get_streaming_graph_service():
    """Get streaming graph service instance."""
    return _streaming_graph_service


def get_streaming_case_controller():
    """Get streaming case controller instance."""
    return _streaming_case_controller


def get_db_config():
    """Get database configuration."""
    if _db_config is None:
        raise RuntimeError("Database config not initialized")
    return _db_config


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
    target_language: Optional[str] = Query(default="ar", description="Target language code"),
    mode: Optional[str] = Query(default="direct", description="Processing mode: 'direct' or 'streaming'")
):
    """WebSocket endpoint for real-time PCM audio streaming with continuous analysis.

    Supports two processing modes:
    - direct: Original mode - immediate classification without LangGraph
    - streaming: New mode - LangGraph streaming workflow with confidence gate

    This endpoint:
    - Receives raw PCM audio frames (16-bit signed, mono, 16kHz)
    - Buffers and processes audio chunks with Faster-Whisper
    - Optionally translates transcripts with GPT-4o-mini
    - Streams partial classification results
    - Sends final summary on session end

    Session Configuration:
        - Can be set via query params (translate, target_language, mode)
        - Or via initial JSON control message

    Message Flow:
        Client -> Server: Binary PCM audio frames OR JSON control message
        Server -> Client: JSON partial results + final summary

    Args:
        websocket: WebSocket connection
        translate: Enable translation (default: True)
        target_language: Target language for translation (default: "ar")
        mode: Processing mode - 'direct' or 'streaming' (default: "direct")
    """
    await websocket.accept()

    # Route to appropriate handler based on mode
    streaming_service = get_streaming_graph_service()

    if mode == "streaming" and streaming_service is not None:
        logger.info(f"WebSocket connection accepted: mode=streaming, translate={translate}")
        await _handle_streaming_mode(websocket, translate, target_language)
    else:
        logger.info(f"WebSocket connection accepted: mode=direct, translate={translate}, target_language={target_language}")
        await _handle_direct_mode(websocket, translate, target_language)


async def _handle_direct_mode(
    websocket: WebSocket,
    translate: bool,
    target_language: str
):
    """Handle WebSocket with direct classification (original mode).

    This is the existing implementation preserved for backward compatibility.
    """
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


async def _handle_streaming_mode(
    websocket: WebSocket,
    translate: bool,
    target_language: str
):
    """Handle WebSocket with streaming LangGraph workflow.

    This mode uses the streaming graph for time-bounded confidence evaluation.
    ALL cases are sent to human review queue - NO auto-dispatch.
    Supports translation toggle and returns both original and translated text.
    """
    audio_service = get_websocket_audio_service()
    streaming_service = get_streaming_graph_service()
    case_controller = get_streaming_case_controller()

    if streaming_service is None:
        logger.error("Streaming service not initialized")
        await websocket.send_json({
            "type": "error",
            "error": "Streaming mode not available",
            "details": "Streaming service not initialized"
        })
        await websocket.close()
        return

    # Create streaming session
    session_state = streaming_service.create_session()
    session_id = session_state.get("session_id")

    # Create audio session for buffering
    audio_session = audio_service.create_session_state(
        translate=translate,
        target_language=target_language
    )

    # Track cumulative translated text for streaming mode
    cumulative_translated_text = ""

    logger.info(f"[WS:STREAMING] Session {session_id} started, translate={translate}")

    # Send session started message
    await websocket.send_json({
        "type": "session_started",
        "session_id": session_id,
        "mode": "streaming",
        "translate": translate,
        "target_language": target_language,
        "evaluation_window_seconds": session_state.get("evaluation_window_seconds", 10.0),
        "confidence_threshold": session_state.get("confidence_threshold", 0.75)
    })

    try:
        async for message in websocket.iter_bytes():
            try:
                # Check for JSON control message
                try:
                    control_data = json.loads(message.decode('utf-8'))
                    if control_data.get("type") == "control":
                        translate = control_data.get("translate", translate)
                        target_language = control_data.get("target_language", target_language)
                        audio_session["translate"] = translate
                        audio_session["target_language"] = target_language
                        logger.info(f"[WS:{session_id}] Control message: translate={translate}, target={target_language}")
                        await websocket.send_json({
                            "type": "control_ack",
                            "translate": translate,
                            "target_language": target_language
                        })
                        continue
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass

                # Process binary PCM audio data
                if isinstance(message, bytes):
                    chunk_received_at = datetime.utcnow().isoformat()

                    # Add PCM frames to buffer
                    audio_session["audio_buffer"].extend(message)

                    # Check if buffer is large enough to process
                    if len(audio_session["audio_buffer"]) >= audio_service.min_chunk_size_bytes:
                        # Transcribe audio buffer
                        stt_result = audio_service.transcribe_buffer(audio_session)

                        if stt_result and stt_result.get("text"):
                            # Get original transcript text
                            original_text = stt_result["text"]
                            full_original = stt_result.get("full_transcript", original_text)
                            detected_language = stt_result.get("detected_language", "ar")

                            # Handle translation if enabled
                            translated_text = None
                            full_translated = None
                            text_for_classification = original_text
                            classification_language = "ar"  # Default to Arabic rules

                            if translate:
                                # Translate the new chunk
                                translated_text = audio_service.translate_text(
                                    text=original_text,
                                    target_language=target_language,
                                    source_language=detected_language
                                )
                                if translated_text:
                                    if cumulative_translated_text:
                                        cumulative_translated_text += " " + translated_text
                                    else:
                                        cumulative_translated_text = translated_text
                                    full_translated = cumulative_translated_text
                                    text_for_classification = translated_text
                                    classification_language = target_language

                            # Update session metrics with STT timing
                            metrics = dict(session_state.get("processing_metrics", {}))
                            metrics["chunk_received_at"] = chunk_received_at
                            metrics["stt_time_ms"] = stt_result.get("stt_time_ms", 0)
                            session_state["processing_metrics"] = metrics

                            # Process through streaming graph
                            session_state, response = streaming_service.process_transcript_chunk(
                                state=session_state,
                                transcript_chunk=text_for_classification,
                                detected_language=classification_language
                            )

                            # Enhance response with transcription section
                            response["transcription"] = {
                                "original_text": full_original,
                                "original_language": detected_language,
                                "translated_text": full_translated,
                                "translated_language": target_language if translate and full_translated else None,
                                "translation_enabled": translate,
                                "text_used_for_classification": text_for_classification,
                                "classification_language": classification_language
                            }

                            # Legacy fields for backward compatibility
                            response["partial_transcript"] = full_original
                            response["detected_language"] = detected_language
                            if translate and full_translated:
                                response["partial_translated_text"] = full_translated
                                response["translated_language"] = target_language

                            # Send response to client
                            await websocket.send_json(response)

                            # Check if streaming should exit
                            if not streaming_service.should_continue(session_state):
                                logger.info(f"[WS:{session_id}] Streaming complete: "
                                            f"{session_state.get('exit_reason')}")

                                # Save to database
                                if case_controller:
                                    db_result = case_controller.store_streaming_case(session_state)
                                    logger.info(f"[WS:{session_id}] Saved to DB: {db_result.get('success')}")

                                # Break the loop - session is complete
                                break

                        # Clear processed audio from buffer
                        audio_session["audio_buffer"].clear()

            except Exception as e:
                logger.error(f"[WS:{session_id}] Error processing message: {e}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "error": str(e),
                    "details": "Error processing audio data"
                })

    except WebSocketDisconnect:
        logger.info(f"[WS:{session_id}] Disconnected by client")

        # If session not complete, save what we have
        if streaming_service.should_continue(session_state):
            session_state["exit_reason"] = "disconnect"
            session_state["review_priority"] = "high"
            session_state["requires_human_review"] = True
            if case_controller:
                case_controller.store_streaming_case(session_state)

    except Exception as e:
        logger.error(f"[WS:{session_id}] WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e),
                "details": "Unexpected WebSocket error"
            })
        except:
            pass

    finally:
        # Clean up session
        streaming_service.end_session(session_id)

        # Close connection
        try:
            await websocket.close()
            logger.info(f"[WS:{session_id}] Connection closed")
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


def init_streaming_services(graph_service, case_controller):
    """Initialize streaming graph services.

    Args:
        graph_service: StreamingGraphService instance
        case_controller: StreamingCaseController instance
    """
    global _streaming_graph_service, _streaming_case_controller

    _streaming_graph_service = graph_service
    _streaming_case_controller = case_controller

    logger.info("WebSocket audio router initialized with streaming services")
