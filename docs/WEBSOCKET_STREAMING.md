# WebSocket Real-Time PCM Audio Streaming

## Overview

This document describes the WebSocket implementation for real-time PCM audio streaming with continuous partial results. This feature extends the existing emergency dispatch system to support live audio streaming, enabling real-time transcription, translation, and classification.

---

## 🎯 Features

- **Real-time PCM audio streaming** over WebSocket
- **Continuous partial results** during audio processing
- **Automatic buffering and chunking** for optimal STT performance
- **Optional translation** using GPT-4o-mini
- **Live classification updates** using existing classifiers
- **Final summary** matching `live_audio_analyze` endpoint format
- **Same classification logic** as HTTP endpoint (single-pass with correct text selection)

---

## 📡 WebSocket Endpoint

### **Endpoint URL**
```
ws://localhost:8000/ws/live-audio-stream
```

### **Query Parameters (Optional)**
- `translate` (boolean, default: `true`) - Enable transcript translation
- `target_language` (string, default: `"ar"`) - Target language for translation

### **Alternative: Control Message**
Instead of query parameters, send an initial JSON control message:
```json
{
  "type": "control",
  "translate": true,
  "target_language": "ar"
}
```

---

## 🎤 PCM Audio Format Requirements

### **Specification**
- **Encoding**: Linear PCM
- **Bit Depth**: 16-bit signed
- **Channels**: Mono (1 channel)
- **Sample Rate**: **16000 Hz** (recommended)
- **Byte Order**: Little-endian
- **Frame Duration**: 10-100 ms (recommended)

### **Example: 100ms Frame**
At 16 kHz, 16-bit mono:
- Samples per frame: `16000 Hz × 0.1 sec = 1600 samples`
- Bytes per frame: `1600 samples × 2 bytes = 3200 bytes`

### **Buffering Strategy**
- Audio frames are buffered until minimum chunk size is reached
- Default minimum: **16000 bytes** (~0.5 seconds)
- Chunks are processed as **1.0 second** segments (configurable in `config.yaml`)

---

## 📨 Message Flow

### **Client → Server**

#### **1. Initial Control Message (Optional)**
```json
{
  "type": "control",
  "translate": true,
  "target_language": "ar"
}
```

#### **2. Binary PCM Audio Frames**
- Send raw PCM audio bytes as binary WebSocket messages
- Frames can be any size (10-100ms recommended)
- Server buffers and processes automatically

### **Server → Client**

#### **1. Session Started (Optional)**
Sent after receiving control message:
```json
{
  "type": "session_started",
  "translate": true,
  "target_language": "ar",
  "message": "Session configured successfully"
}
```

#### **2. Partial Results**
Sent periodically as audio is processed:
```json
{
  "type": "partial",
  "segment_index": 1,
  "timestamp": "2025-12-09T10:30:45.123456",
  "partial_transcript": "There's a fire in my house",
  "detected_language": "en",
  "partial_translated_text": "يوجد حريق في منزلي",
  "translated_language": "ar",
  "audio_duration_seconds": 2.5,
  "classification": {
    "incident": {
      "incident_type": "FIRE",
      "confidence": 0.95,
      "reasoning": "تم اكتشاف كلمات مرتبطة بالحريق",
      "keywords_found": ["حريق", "منزل"]
    },
    "severity": {
      "severity_level": "HIGH",
      "confidence": 0.92,
      "reasoning": "حالة خطيرة محتملة",
      "urgency_indicators": ["حريق"]
    },
    "dispatch": {
      "dispatch_unit": "FIRE",
      "confidence": 0.98,
      "reasoning": "يتطلب الحريق فرقة إطفاء",
      "estimated_priority": "Priority 1"
    }
  }
}
```

#### **3. Final Summary**
Sent when session ends:
```json
{
  "type": "final",
  "timestamp": "2025-12-09T10:30:50.987654",
  "session_duration_seconds": 5.5,
  "total_segments": 3,
  "original_transcript": "There's a fire in my house and it's spreading quickly",
  "detected_language": "en",
  "translated_text": "يوجد حريق في منزلي وينتشر بسرعة",
  "translated_language": "ar",
  "classification": {
    "incident": { ... },
    "severity": { ... },
    "dispatch": { ... }
  }
}
```

#### **4. Error Messages**
```json
{
  "type": "error",
  "error": "Error description",
  "details": "Additional error context"
}
```

---

## 🔄 Classification Logic

The WebSocket implementation uses the **same classification logic** as the HTTP `/api/live-audio-analyze` endpoint:

### **Text Selection Rule**
```python
if translate:
    text_for_classification = translated_text
    language_for_classification = target_language
else:
    text_for_classification = original_transcript
    language_for_classification = detected_language
```

### **Key Points**
- ✅ **Single-pass classification** (not duplicated)
- ✅ Classification happens on **accumulated text** (grows with each segment)
- ✅ Rules loaded from `config/emergency_rules/{language}/`
- ✅ Classification results and reasoning in the **correct language**
- ✅ Partial updates show **progressive classification** as more context becomes available

---

## 🏗️ Architecture

### **Service Layer**
**`services/websocket_audio_service.py`**
- Handles PCM audio buffering
- Converts PCM to format for Faster-Whisper
- Manages session state (transcripts, language, config)
- Processes audio chunks with streaming STT
- Optionally translates segments
- Runs classification on accumulated text
- Generates partial and final results

### **API Layer**
**`api/websocket_audio_router.py`**
- Thin WebSocket router following MVC pattern
- Accepts connections with session parameters
- Receives PCM audio frames
- Delegates processing to service layer
- Streams JSON results to client
- Handles errors and connection cleanup

### **Integration**
**`main.py`**
- Creates `WebSocketAudioService` instance
- Initializes with existing `TranslationModel` and classifiers
- Registers WebSocket router
- Shares infrastructure with `live_audio_analyze` endpoint

---

## 📁 Files Added/Modified

### **New Files**
1. `services/websocket_audio_service.py` - Streaming audio processing service
2. `api/websocket_audio_router.py` - WebSocket endpoint
3. `WEBSOCKET_STREAMING.md` - This documentation

### **Modified Files**
1. `main.py` - Added WebSocket service initialization and router registration
2. `config/config.yaml` - Added WebSocket-specific configuration

---

## ⚙️ Configuration

### **Config Settings (`config/config.yaml`)**

```yaml
whisper:
  # ... existing settings ...

  # WebSocket Streaming Settings
  sample_rate: 16000                  # PCM sample rate in Hz
  chunk_duration_seconds: 1.0         # Target chunk duration for processing
  min_chunk_size_bytes: 16000         # Minimum buffer size (~0.5 sec)
```

### **Adjusting Buffer Settings**

**For faster responses (more frequent partial updates):**
```yaml
min_chunk_size_bytes: 8000          # ~0.25 seconds
chunk_duration_seconds: 0.5
```

**For better accuracy (longer context):**
```yaml
min_chunk_size_bytes: 32000         # ~1.0 seconds
chunk_duration_seconds: 2.0
```

---

## 🚀 Usage Examples

### **Python Client Example**

```python
import asyncio
import websockets
import json
import wave

async def stream_audio():
    # Connect to WebSocket
    uri = "ws://localhost:8000/ws/live-audio-stream?translate=true&target_language=ar"

    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")

        # Open audio file (16kHz, 16-bit, mono PCM)
        with wave.open("emergency_call.wav", "rb") as wav_file:
            # Verify format
            assert wav_file.getnchannels() == 1, "Must be mono"
            assert wav_file.getsampwidth() == 2, "Must be 16-bit"
            assert wav_file.getframerate() == 16000, "Must be 16kHz"

            # Stream audio in chunks
            chunk_size = 3200  # 100ms at 16kHz

            while True:
                pcm_data = wav_file.readframes(chunk_size // 2)  # readframes takes samples, not bytes
                if not pcm_data:
                    break

                # Send PCM data
                await websocket.send(pcm_data)
                print(f"Sent {len(pcm_data)} bytes")

                # Check for responses (non-blocking)
                try:
                    response = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=0.1
                    )
                    result = json.loads(response)

                    if result["type"] == "partial":
                        print(f"\n[Partial {result['segment_index']}]")
                        print(f"Transcript: {result['partial_transcript']}")
                        if "partial_translated_text" in result:
                            print(f"Translation: {result['partial_translated_text']}")
                        print(f"Incident: {result['classification']['incident']['incident_type']}")

                    elif result["type"] == "final":
                        print(f"\n[FINAL]")
                        print(f"Full Transcript: {result['original_transcript']}")
                        if "translated_text" in result:
                            print(f"Full Translation: {result['translated_text']}")
                        print(f"Classification: {result['classification']}")

                except asyncio.TimeoutError:
                    continue

        # Close connection (triggers final result)
        await websocket.close()
        print("\nConnection closed")

# Run client
asyncio.run(stream_audio())
```

### **JavaScript Client Example**

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live-audio-stream?translate=true&target_language=ar');

ws.onopen = () => {
  console.log('WebSocket connected');

  // Get microphone access
  navigator.mediaDevices.getUserMedia({ audio: {
    sampleRate: 16000,
    channelCount: 1,
    echoCancellation: true
  }}).then(stream => {
    const audioContext = new AudioContext({ sampleRate: 16000 });
    const source = audioContext.createMediaStreamSource(stream);
    const processor = audioContext.createScriptProcessor(4096, 1, 1);

    processor.onaudioprocess = (e) => {
      const inputData = e.inputBuffer.getChannelData(0);

      // Convert Float32 [-1, 1] to Int16 PCM
      const pcmData = new Int16Array(inputData.length);
      for (let i = 0; i < inputData.length; i++) {
        pcmData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
      }

      // Send PCM data
      ws.send(pcmData.buffer);
    };

    source.connect(processor);
    processor.connect(audioContext.destination);
  });
};

ws.onmessage = (event) => {
  const result = JSON.parse(event.data);

  if (result.type === 'partial') {
    console.log('Partial:', result.partial_transcript);
    console.log('Incident:', result.classification.incident.incident_type);
  } else if (result.type === 'final') {
    console.log('Final:', result.original_transcript);
    console.log('Classification:', result.classification);
  }
};

ws.onerror = (error) => console.error('WebSocket error:', error);
ws.onclose = () => console.log('WebSocket closed');
```

---

## 🔍 Testing

### **Test WebSocket Info Endpoint**
```bash
curl http://localhost:8000/ws/info
```

This returns detailed information about the WebSocket endpoint, PCM format, and message schemas.

### **Test with Python Client**
```bash
python test_websocket_client.py
```

### **Test with wscat CLI Tool**
```bash
# Install wscat
npm install -g wscat

# Connect
wscat -c "ws://localhost:8000/ws/live-audio-stream?translate=true&target_language=ar"

# Send control message
{"type": "control", "translate": true, "target_language": "ar"}

# Then send binary PCM data (requires file streaming tool)
```

---

## 🔧 Integration with Existing System

### **Shared Components**
The WebSocket implementation **reuses** existing components:

1. **TranslationModel** (`models/translation_model.py`)
   - Same translation logic as `live_audio_analyze`
   - GPT-4o-mini for cost-effective translation

2. **Classifiers** (`models/*_classifier.py`)
   - IncidentClassifier
   - SeverityClassifier
   - DispatchClassifier
   - Same rules from `config/emergency_rules/{language}/`

3. **Faster-Whisper** (CTranslate2)
   - Shared Whisper model instance (lazy-loaded)
   - Same configuration from `config.yaml`

### **Differences from HTTP Endpoint**

| Feature | `/api/live-audio-analyze` (HTTP) | `/ws/live-audio-stream` (WebSocket) |
|---------|----------------------------------|-------------------------------------|
| Input | Complete audio file | Streaming PCM frames |
| Processing | Single-shot | Continuous buffering + chunking |
| Output | Single final result | Partial results + final summary |
| Connection | Request-response | Persistent connection |
| Use Case | Batch analysis | Real-time streaming |

### **Same Classification Behavior**
Both endpoints follow the **identical classification logic**:
- ✅ Text selection: `translated_text` if translate=True, else `original_transcript`
- ✅ Language selection: `target_language` if translate=True, else `detected_language`
- ✅ Single-pass classification
- ✅ Same rule files
- ✅ Same response structure

---

## 📊 Performance Considerations

### **Latency**
- **Audio buffering**: ~0.5-1.0 seconds (configurable)
- **Whisper transcription**: ~0.2-0.5 seconds per chunk (base model on CPU)
- **Translation** (if enabled): ~0.3-0.8 seconds per segment
- **Classification**: ~0.5-1.0 seconds (3 classifiers)
- **Total per segment**: ~1.5-3.0 seconds

### **Optimization Tips**

1. **Use GPU for Whisper**
   ```yaml
   whisper:
     device: "cuda"
     compute_type: "float16"
   ```

2. **Adjust chunk size**
   - Smaller chunks = faster partial results, less accuracy
   - Larger chunks = better accuracy, slower updates

3. **Disable translation for faster processing**
   ```
   ws://localhost:8000/ws/live-audio-stream?translate=false
   ```

4. **Use smaller Whisper model**
   ```yaml
   whisper:
     model_size: "tiny"  # Fastest, less accurate
   ```

---

## 🐛 Error Handling

### **Common Errors**

#### **1. Service Not Initialized**
```json
{
  "type": "error",
  "error": "WebSocket audio service not initialized",
  "details": "..."
}
```
**Solution**: Ensure `main.py` properly initializes the service.

#### **2. Classification Failed**
```json
{
  "type": "error",
  "error": "Classification failed: ...",
  "details": "Error processing audio data"
}
```
**Solution**: Check classifier configuration and rule files.

#### **3. Buffer Too Small**
No partial result sent (buffer waiting for more data).
**Solution**: Send more audio or adjust `min_chunk_size_bytes`.

### **Graceful Degradation**
- If partial processing fails, session continues
- Final result always sent (even with errors)
- Errors don't terminate connection (unless fatal)

---

## 📝 Summary

### **What Was Added**
- WebSocket endpoint for real-time PCM audio streaming
- Service layer for buffering, chunking, and streaming STT
- Continuous partial results with progressive classification
- Final summary matching HTTP endpoint format

### **How It Works**
1. Client connects with session parameters (translate, target_language)
2. Client streams PCM audio frames
3. Server buffers and processes chunks
4. Server sends partial JSON results
5. On disconnect, server sends final summary

### **Key Benefits**
- ✅ Real-time transcription and classification
- ✅ Progressive updates as audio streams
- ✅ Reuses existing translation and classification logic
- ✅ Consistent with HTTP endpoint behavior
- ✅ Configurable buffering and chunking
- ✅ Production-ready error handling

---

## 🔗 Related Documentation
- `LIVE_AUDIO_WORKFLOW.md` - HTTP endpoint documentation
- `config/config.yaml` - Configuration reference
- `CRUD_OPERATIONS.md` - API documentation

---

**Implementation Status**: ✅ Complete and Production-Ready
