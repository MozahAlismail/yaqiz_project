# Installation and Setup Guide

## Prerequisites

1. Python 3.10 or higher
2. PostgreSQL 12+ (database)
3. OpenAI API key
4. Git

**Note:** This project now uses OpenAI's cloud API for audio transcription. No local ML models or FFmpeg required! 🎉

## Step-by-Step Installation

### 1. Install PostgreSQL

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**On macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**On Windows:**
Download from https://www.postgresql.org/download/windows/

### 2. Clone or Navigate to Project

```bash
cd /path/to/project
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies (Simple & Fast!)

```bash
pip install -r requirements.txt
```

**Installation is now much faster!** No PyTorch, TensorFlow, or heavy ML libraries needed.
All AI processing happens via OpenAI's cloud API.

### 5. Configure Database Connection

Create a .env file:
```bash
cp .env.example .env
```

Edit .env and configure your database and API settings:
```
# OpenAI API
OPENAI_API_KEY=your-actual-api-key-here

# PostgreSQL Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=emergency_dispatch
DB_USER=postgres
DB_PASSWORD=your-postgres-password
```

Or export environment variables directly:
```bash
export OPENAI_API_KEY=your-actual-api-key-here
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=emergency_dispatch
export DB_USER=postgres
export DB_PASSWORD=postgres
```

### 6. Initialize PostgreSQL Database

```bash
python data/init_db.py
```

This will:
- Create the database if it doesn't exist
- Create the cases and feedback tables
- Create necessary indexes

### 7. Start the Server

**Option A: Using the run script**
```bash
chmod +x run.sh
./run.sh
```

**Option B: Direct Python**
```bash
python main.py
```

**Option C: Using uvicorn**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 8. Verify Installation

Open browser and go to:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/api/health (Health check)

## Docker Installation (Alternative)

### 1. Build Docker Image

```bash
docker build -t emergency-dispatch-ai .
```

### 2. Run Container

```bash
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key emergency-dispatch-ai
```

### 3. Or Use Docker Compose

```bash
export OPENAI_API_KEY=your-key
docker-compose up
```

## Testing the Installation

### 1. Run Tests

```bash
pytest
```

### 2. Test API Endpoints

```bash
chmod +x test_api.sh
./test_api.sh
```

### 3. Manual API Test

```bash
# Health check
curl http://localhost:8000/api/health

# Analyze audio (requires audio file)
curl -X POST "http://localhost:8000/api/analyze-audio" \
  -F "audio_file=@sample_audio.wav"
```

## Troubleshooting

### Issue: Import errors
**Solution:** Make sure all dependencies are installed
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Database errors
**Solution:** Reinitialize databases
```bash
python data/init_db.py
```

### Issue: OpenAI API errors
**Solution:** Check API key is set correctly
```bash
echo $OPENAI_API_KEY
```

## Configuration

Edit `config/config.yaml` to customize:
- Model settings
- Database paths
- Agent parameters
- RLHF settings
- Logging configuration

## Next Steps

1. Review the README.md for API documentation
2. Explore the Swagger UI at /docs
3. Test with sample audio files
4. Review and customize rule files in config/emergency_rules/
5. Set up monitoring and logging

## Production Deployment

For production deployment:
1. Use HTTPS/TLS
2. Set up proper authentication
3. Use production database (PostgreSQL)
4. Configure rate limiting
5. Set up monitoring and alerting
6. Enable backup strategies
7. Use process manager (e.g., supervisor, systemd)
8. Configure reverse proxy (nginx, traefik)

## Support

For issues, check:
1. Logs in logs/app.log
2. GitHub issues
3. Documentation in README.md
