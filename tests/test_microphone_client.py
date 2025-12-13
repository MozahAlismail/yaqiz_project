"""
Microphone WebSocket Test Client

Captures audio from laptop microphone and streams to WebSocket endpoint
for testing the streaming LangGraph workflow.

Requirements:
    pip install websockets pyaudio

Usage:
    python tests/test_microphone_client.py                    # Default: streaming mode, auto-detect language
    python tests/test_microphone_client.py --language auto    # Auto-detect language (Whisper decides)
    python tests/test_microphone_client.py --language ar      # Force Arabic language detection
    python tests/test_microphone_client.py --language en      # Force English language detection
    python tests/test_microphone_client.py --mode streaming   # Streaming mode
    python tests/test_microphone_client.py --mode direct      # Direct mode (original behavior)
    python tests/test_microphone_client.py --translate        # Enable translation to Arabic
    python tests/test_microphone_client.py --translate --target-language en  # Translate to English

Audio Format:
    - Linear PCM, 16-bit signed, Mono
    - Sample rate: 16000 Hz
    - Frame duration: 100ms chunks

Note:
    Translation is DISABLED by default. Use --translate to enable.
    Use --language to force detected language (ar, en) or 'auto' for auto-detect. Default is 'auto'.
"""

import asyncio
import argparse
import json
import sys
import signal
from datetime import datetime

try:
    import websockets
except ImportError:
    print("Error: websockets not installed")
    print("Run: pip install websockets")
    sys.exit(1)

try:
    import pyaudio
except ImportError:
    print("Error: pyaudio not installed")
    print("Run: pip install pyaudio")
    print("Note: On Windows, you may need: pip install pipwin && pipwin install pyaudio")
    sys.exit(1)


# Audio configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION_MS = 100
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)
FORMAT = pyaudio.paInt16


class MicrophoneStreamingClient:
    """WebSocket client for streaming microphone audio."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        mode: str = "streaming",
        translate: bool = False,
        target_language: str = "ar",
        language: str = "auto"
    ):
        """Initialize the microphone client.

        Args:
            host: Server hostname
            port: Server port
            mode: Processing mode ('streaming' or 'direct')
            translate: Enable translation (disabled by default)
            target_language: Target language for translation (when enabled)
            language: Force detected language ('ar', 'en') or 'auto' for auto-detect
        """
        self.host = host
        self.port = port
        self.mode = mode
        self.translate = translate
        self.target_language = target_language
        self.language = language

        # Build WebSocket URI - only add language param if not auto
        base_uri = (
            f"ws://{host}:{port}/ws/live-audio-stream"
            f"?mode={mode}&translate={str(translate).lower()}"
            f"&target_language={target_language}"
        )

        # Add language parameter (server handles 'auto' as None)
        if language and language != "auto":
            self.uri = f"{base_uri}&language={language}"
        else:
            self.uri = base_uri  # No language param = auto-detect

        self.running = False
        self.audio = None
        self.stream = None
        self.start_time = None

    def _init_audio(self):
        """Initialize PyAudio and microphone stream."""
        self.audio = pyaudio.PyAudio()

        # Get default input device info
        try:
            info = self.audio.get_default_input_device_info()
            print(f"Microphone: {info['name']}")
        except Exception as e:
            print(f"Warning: Could not get device info: {e}")

        # Open microphone stream
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )

    def _cleanup_audio(self):
        """Clean up audio resources."""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
        if self.audio:
            try:
                self.audio.terminate()
            except Exception:
                pass

    async def run(self):
        """Main run loop - connect and stream audio."""
        print("\n" + "=" * 60)
        print("MICROPHONE STREAMING TEST CLIENT")
        print("=" * 60)
        print(f"Server: {self.uri}")
        print(f"Mode: {self.mode}")
        if self.language == "auto":
            print("Language: auto-detect (Whisper will detect)")
        else:
            print(f"Language: {self.language} (forced)")
        print(f"Translate: {self.translate} -> {self.target_language}")
        print("Press Ctrl+C to stop\n")

        try:
            async with websockets.connect(self.uri) as websocket:
                print("Connected to server!")
                print("Speak now...\n")

                self._init_audio()
                self.running = True
                self.start_time = datetime.now()

                # Create tasks for sending and receiving
                send_task = asyncio.create_task(self._send_audio(websocket))
                receive_task = asyncio.create_task(self._receive_messages(websocket))

                # Wait for either task to complete
                done, pending = await asyncio.wait(
                    [send_task, receive_task],
                    return_when=asyncio.FIRST_COMPLETED
                )

                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

        except websockets.exceptions.ConnectionRefused:
            print(f"\nConnection refused! Is the server running at {self.host}:{self.port}?")
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            self._cleanup_audio()
            print("\nSession ended.")

    async def _send_audio(self, websocket):
        """Send audio chunks to server."""
        try:
            while self.running:
                # Read audio from microphone
                try:
                    data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    await websocket.send(data)
                except Exception as e:
                    if self.running:
                        print(f"Audio read error: {e}")
                    break

                # Small delay to prevent overwhelming
                await asyncio.sleep(CHUNK_DURATION_MS / 1000 * 0.9)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Send error: {e}")

    async def _receive_messages(self, websocket):
        """Receive and display messages from server."""
        try:
            async for message in websocket:
                try:
                    result = json.loads(message)
                    self._display_result(result)

                    # Check if final result
                    if result.get("is_final") or result.get("type") == "final":
                        self.running = False
                        break

                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")

        except websockets.exceptions.ConnectionClosed:
            print("\nConnection closed by server")
            self.running = False
        except asyncio.CancelledError:
            pass

    def _display_result(self, result: dict):
        """Display result in a formatted way."""
        result_type = result.get("type", "unknown")

        # Clear line and display
        print(" " * 80, end="\r")

        if result_type == "partial":
            self._display_partial(result)
        elif result_type == "final":
            self._display_final(result)
        elif result_type == "session_started":
            lang_mode = result.get('language_mode', 'unknown')
            lang = result.get('language') or 'auto-detect'
            print(f"Session started:")
            print(f"  Language: {lang} ({lang_mode})")
            print(f"  Translate: {result.get('translate')} -> {result.get('target_language')}")
        elif result_type == "error":
            print(f"ERROR: {result.get('error')}")
        else:
            print(f"Unknown message type: {result_type}")

    def _display_partial(self, result: dict):
        """Display partial result."""
        chunk_count = result.get("chunk_count", 0)
        evaluation = result.get("evaluation", {})

        print(f"\n--- PARTIAL #{chunk_count} ---")
        print(f"Time: {evaluation.get('elapsed_seconds', 0):.1f}s / "
              f"{evaluation.get('window_seconds', 10)}s")
        print(f"Confidence: {evaluation.get('overall_confidence', 0):.1%}")

        # Show transcript (truncated)
        transcript = result.get("transcript", "")
        if len(transcript) > 60:
            transcript = transcript[-60:] + "..."
        print(f"Transcript: {transcript}")

        # Show classification
        classification = result.get("classification", {})
        incident = classification.get("incident", {})
        severity = classification.get("severity", {})
        dispatch = classification.get("dispatch", {})

        print(f"Incident: {incident.get('type', '?')} "
              f"({incident.get('confidence', 0):.0%})")
        print(f"Severity: {severity.get('level', '?')} "
              f"({severity.get('confidence', 0):.0%})")
        print(f"Dispatch: {dispatch.get('unit', '?')} "
              f"({dispatch.get('confidence', 0):.0%})")

    def _display_final(self, result: dict):
        """Display final result."""
        evaluation = result.get("evaluation", {})
        classification = result.get("classification", {})

        exit_reason = evaluation.get("exit_reason", "unknown")
        priority = evaluation.get("review_priority", "normal")

        # Priority icons
        icons = {"urgent": "!!!", "high": "!!", "normal": "."}
        icon = icons.get(priority, "?")

        print("\n" + "=" * 60)
        print(f"FINAL RESULT [{icon} {priority.upper()}]")
        print("=" * 60)

        print(f"\nExit Reason: {exit_reason}")
        print(f"Review Priority: {priority}")
        print(f"Total Time: {evaluation.get('elapsed_seconds', 0):.1f}s")
        print(f"Overall Confidence: {evaluation.get('overall_confidence', 0):.1%}")
        print(f"Requires Review: {evaluation.get('requires_human_review', True)}")

        print(f"\n--- Transcript ---")
        transcript = result.get("transcript", "")
        print(transcript[:500] if len(transcript) > 500 else transcript)

        print(f"\n--- Classification ---")
        incident = classification.get("incident", {})
        severity = classification.get("severity", {})
        dispatch = classification.get("dispatch", {})

        print(f"Incident: {incident.get('type', 'UNKNOWN')} "
              f"({incident.get('confidence', 0):.0%})")
        print(f"  Reasoning: {incident.get('reasoning', '')[:100]}")

        print(f"Severity: {severity.get('level', 'UNKNOWN')} "
              f"({severity.get('confidence', 0):.0%})")
        print(f"  Reasoning: {severity.get('reasoning', '')[:100]}")

        print(f"Dispatch: {dispatch.get('unit', 'UNKNOWN')} "
              f"({dispatch.get('confidence', 0):.0%})")
        print(f"  Priority: {dispatch.get('priority', '')}")

        # Show concerns if any
        concerns = evaluation.get("concerns", [])
        if concerns:
            print(f"\n--- Concerns ---")
            for concern in concerns:
                print(f"  - {concern}")

        # Show unsupported language reason if present
        unsupported_reason = result.get("unsupported_language_reason", "")
        if unsupported_reason:
            print(f"\n--- Unsupported Language ---")
            print(unsupported_reason[:300])

        # Show metrics
        metrics = result.get("processing_metrics", {})
        if metrics:
            print(f"\n--- Processing Metrics ---")
            print(f"Total Processing: {metrics.get('total_processing_time_ms', 0):.1f}ms")
            print(f"STT Time: {metrics.get('stt_time_ms', 0):.1f}ms")
            print(f"Classification Time: {metrics.get('classification_total_time_ms', 0):.1f}ms")
            print(f"Chunks Processed: {metrics.get('chunks_processed', 0)}")

        print("\n" + "=" * 60)
        print("Case saved for human review")
        print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Microphone WebSocket Test Client for Emergency Dispatch"
    )
    parser.add_argument(
        "--host", default="localhost",
        help="Server hostname (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--mode", choices=["streaming", "direct"], default="streaming",
        help="Processing mode (default: streaming)"
    )
    parser.add_argument(
        "--language", "-l", choices=["auto", "ar", "en"], default="auto",
        help="Language mode: 'auto' for auto-detect, 'ar' for Arabic, 'en' for English (default: auto)"
    )
    parser.add_argument(
        "--translate", action="store_true",
        help="Enable translation (disabled by default)"
    )
    parser.add_argument(
        "--target-language", default="ar",
        help="Target language for translation when --translate is enabled (default: ar)"
    )

    args = parser.parse_args()

    client = MicrophoneStreamingClient(
        host=args.host,
        port=args.port,
        mode=args.mode,
        translate=args.translate,
        target_language=args.target_language,
        language=args.language
    )

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\nStopping...")
        client.running = False

    signal.signal(signal.SIGINT, signal_handler)

    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("\nInterrupted by user")


if __name__ == "__main__":
    main()
