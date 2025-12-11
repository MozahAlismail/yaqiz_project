# Quick Start Guide

## Prerequisites
- PostgreSQL 12+ installed and running
- Python 3.10+
- OpenAI API key

**Note:** No FFmpeg or local ML models needed! Everything runs via OpenAI API ⚡

## 1-Minute Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your-key-here
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=emergency_dispatch
export DB_USER=postgres
export DB_PASSWORD=postgres123

# Initialize PostgreSQL database
python data/init_db.py

# Run server
python main.py
```

## Test It

```bash
# Visit in browser
http://localhost:8000/docs

# Or test with curl
curl http://localhost:8000/api/health
```

## Use It

### Analyze Audio
```bash
curl -X POST "http://localhost:8000/api/analyze-audio" \
  -F "audio_file=@emergency_call.wav"
```

### Submit Feedback
```bash
curl -X POST "http://localhost:8000/api/operator-feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "uuid-from-previous-call",
    "corrected_incident": "FIRE",
    "corrected_severity": "CRITICAL"
  }'
```

### Retrain Model
```bash
curl -X POST "http://localhost:8000/api/retrain-model"
```

## That's It!

For more details, see:
- README.md - Full documentation
- INSTALLATION_GUIDE.md - Detailed setup
- PROJECT_STRUCTURE.md - Architecture
- /docs endpoint - API documentation
