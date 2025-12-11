"""
WebSocket Audio Streaming Test Client

This script demonstrates how to stream PCM audio to the WebSocket endpoint
and receive continuous partial results.

Requirements:
    pip install websockets

Usage:
    python test_websocket_client.py [audio_file.wav] [--translate] [--target-language ar]
"""

import asyncio
import websockets
import json
import wave
import sys
import argparse
from pathlib import Path


async def stream_audio_file(
    audio_path: str,
    translate: bool = True,
    target_language: str = "ar",
    chunk_duration_ms: int = 100
):
    """Stream audio file to WebSocket endpoint.

    Args:
        audio_path: Path to WAV file (must be 16kHz, 16-bit, mono)
        translate: Enable translation
        target_language: Target language for translation
        chunk_duration_ms: Duration of each chunk in milliseconds
    """
    # Build WebSocket URI with query parameters
    uri = f"ws://localhost:8000/ws/live-audio-stream?translate={str(translate).lower()}&target_language={target_language}"

    print(f"Connecting to: {uri}")
    print(f"Audio file: {audio_path}")
    print(f"Translation: {'Enabled' if translate else 'Disabled'}")
    if translate:
        print(f"Target language: {target_language}")
    print("-" * 60)

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket\n")

            # Open and validate WAV file
            try:
                with wave.open(audio_path, "rb") as wav_file:
                    # Validate format
                    channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()
                    frame_rate = wav_file.getframerate()
                    n_frames = wav_file.getnframes()

                    print(f"Audio Format:")
                    print(f"  Channels: {channels}")
                    print(f"  Bit Depth: {sample_width * 8}-bit")
                    print(f"  Sample Rate: {frame_rate} Hz")
                    print(f"  Duration: {n_frames / frame_rate:.2f} seconds")

                    if channels != 1:
                        print("⚠️  Warning: Audio should be mono (1 channel)")
                    if sample_width != 2:
                        print("⚠️  Warning: Audio should be 16-bit (2 bytes)")
                    if frame_rate != 16000:
                        print("⚠️  Warning: Audio should be 16kHz sample rate")

                    print("-" * 60)

                    # Calculate chunk size
                    # chunk_duration_ms milliseconds of audio
                    samples_per_chunk = int(frame_rate * chunk_duration_ms / 1000)
                    bytes_per_chunk = samples_per_chunk * sample_width

                    print(f"Streaming audio ({chunk_duration_ms}ms chunks)...\n")

                    # Stream audio in chunks
                    chunk_count = 0
                    partial_count = 0

                    while True:
                        # Read chunk
                        pcm_data = wav_file.readframes(samples_per_chunk)
                        if not pcm_data:
                            break

                        chunk_count += 1

                        # Send PCM data
                        await websocket.send(pcm_data)
                        print(f"📤 Sent chunk {chunk_count}: {len(pcm_data)} bytes")

                        # Check for responses (non-blocking)
                        try:
                            response = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=0.05
                            )
                            result = json.loads(response)

                            if result["type"] == "session_started":
                                print(f"\n✅ {result['message']}")
                                print("-" * 60)

                            elif result["type"] == "partial":
                                partial_count += 1
                                print(f"\n{'='*60}")
                                print(f"📊 PARTIAL RESULT #{result['segment_index']}")
                                print(f"{'='*60}")
                                print(f"Timestamp: {result['timestamp']}")
                                print(f"Duration: {result['audio_duration_seconds']:.2f}s")
                                print(f"\n🎤 Original Transcript:")
                                print(f"   Language: {result['detected_language']}")
                                print(f"   Text: {result['partial_transcript']}")

                                if "partial_translated_text" in result:
                                    print(f"\n🌐 Translation ({result['translated_language']}):")
                                    print(f"   {result['partial_translated_text']}")

                                classification = result['classification']
                                print(f"\n📋 Classification:")
                                print(f"   Incident: {classification['incident']['incident_type']} "
                                      f"({classification['incident']['confidence']:.2f})")
                                print(f"   Severity: {classification['severity']['severity_level']} "
                                      f"({classification['severity']['confidence']:.2f})")
                                print(f"   Dispatch: {classification['dispatch']['dispatch_unit']} "
                                      f"({classification['dispatch']['confidence']:.2f})")
                                print("-" * 60 + "\n")

                            elif result["type"] == "error":
                                print(f"\n❌ ERROR: {result['error']}")
                                print(f"   Details: {result.get('details', 'N/A')}\n")

                        except asyncio.TimeoutError:
                            # No response yet, continue streaming
                            continue

                    print(f"\n✅ Finished streaming {chunk_count} chunks")
                    print("⏳ Waiting for final result...")

            except FileNotFoundError:
                print(f"❌ Error: Audio file not found: {audio_path}")
                return
            except wave.Error as e:
                print(f"❌ Error: Invalid WAV file: {e}")
                return

            # Wait for final result
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                result = json.loads(response)

                if result["type"] == "final":
                    print(f"\n{'='*60}")
                    print(f"🏁 FINAL RESULT")
                    print(f"{'='*60}")
                    print(f"Timestamp: {result['timestamp']}")
                    print(f"Session Duration: {result['session_duration_seconds']:.2f}s")
                    print(f"Total Segments: {result['total_segments']}")

                    print(f"\n🎤 Complete Original Transcript:")
                    print(f"   Language: {result['detected_language']}")
                    print(f"   Text: {result['original_transcript']}")

                    if "translated_text" in result:
                        print(f"\n🌐 Complete Translation ({result['translated_language']}):")
                        print(f"   {result['translated_text']}")

                    classification = result['classification']
                    print(f"\n📋 Final Classification:")
                    print(f"   Incident: {classification['incident']['incident_type']} "
                          f"(Confidence: {classification['incident']['confidence']:.2%})")
                    print(f"   Reasoning: {classification['incident']['reasoning']}")
                    print(f"\n   Severity: {classification['severity']['severity_level']} "
                          f"(Confidence: {classification['severity']['confidence']:.2%})")
                    print(f"   Reasoning: {classification['severity']['reasoning']}")
                    print(f"\n   Dispatch: {classification['dispatch']['dispatch_unit']} "
                          f"(Confidence: {classification['dispatch']['confidence']:.2%})")
                    print(f"   Priority: {classification['dispatch']['estimated_priority']}")
                    print(f"   Reasoning: {classification['dispatch']['reasoning']}")
                    print("=" * 60)

                    print(f"\n✅ Session completed successfully!")
                    print(f"   Total partial results: {partial_count}")

            except asyncio.TimeoutError:
                print("⚠️  Timeout waiting for final result")

    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ WebSocket error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="WebSocket Audio Streaming Test Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stream with translation to Arabic (default)
  python test_websocket_client.py audio/emergency.wav

  # Stream without translation
  python test_websocket_client.py audio/emergency.wav --no-translate

  # Stream with translation to English
  python test_websocket_client.py audio/emergency.wav --target-language en

  # Use smaller chunks for faster partial results
  python test_websocket_client.py audio/emergency.wav --chunk-duration 50
        """
    )

    parser.add_argument(
        "audio_file",
        nargs="?",
        default="audio/emergency.wav",
        help="Path to WAV audio file (16kHz, 16-bit, mono)"
    )

    parser.add_argument(
        "--translate",
        dest="translate",
        action="store_true",
        default=True,
        help="Enable translation (default)"
    )

    parser.add_argument(
        "--no-translate",
        dest="translate",
        action="store_false",
        help="Disable translation"
    )

    parser.add_argument(
        "--target-language",
        default="ar",
        help="Target language for translation (default: ar)"
    )

    parser.add_argument(
        "--chunk-duration",
        type=int,
        default=100,
        help="Chunk duration in milliseconds (default: 100ms)"
    )

    args = parser.parse_args()

    # Check if file exists
    if not Path(args.audio_file).exists():
        print(f"❌ Error: Audio file not found: {args.audio_file}")
        print(f"\nUsage: python test_websocket_client.py [audio_file.wav]")
        sys.exit(1)

    # Run async client
    try:
        asyncio.run(stream_audio_file(
            audio_path=args.audio_file,
            translate=args.translate,
            target_language=args.target_language,
            chunk_duration_ms=args.chunk_duration
        ))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
