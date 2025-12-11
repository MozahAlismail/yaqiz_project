"""Audio Analysis Router

Note: The /analyze-audio endpoint has been removed.
STT is now handled via faster-whisper services:
- WebSocket endpoint: /ws/live-audio-stream
- HTTP endpoint: /api/realtime-audio-analyze
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["audio"])

# Note: The /analyze-audio endpoint has been removed.
# For audio analysis, use:
# - WebSocket: /ws/live-audio-stream (real-time streaming)
# - HTTP: /api/realtime-audio-analyze (file upload with faster-whisper)
