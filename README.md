# AI Emergency Dispatch Assistant

A production-ready multilingual multi-agent AI system for emergency call analysis.

## Features

- Multilingual Support (Arabic + English)
- 6 Specialized AI Agents
- Speech-to-Text using Whisper
- Incident Classification
- Severity Assessment
- Dispatch Recommendation
- Self-Evaluation
- Human-in-the-Loop
- Feedback System with Mini-RLHF
- RESTful API
- PostgreSQL Database

## Prerequisites

- Python 3.10+
- PostgreSQL 12+ (database)
- OpenAI API key (for transcription and LLM)

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-key

# Start all services (PostgreSQL + API)
docker-compose up -d
```

The application will be available at http://localhost:8000

### Option 2: Local Installation

1. **Install PostgreSQL** (if not already installed)
   - Ubuntu/Debian: `sudo apt install postgresql postgresql-contrib`
   - macOS: `brew install postgresql@15`
   - Windows: Download from https://www.postgresql.org/download/

2. **Install Python dependencies** (simple - no FFmpeg or ML models needed!):
```bash
# Install latest versions (recommended)
pip install -r requirements.txt

# OR install pinned versions (for reproducibility)
pip install -r requirements-pinned.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your database credentials and API key
```

4. **Initialize PostgreSQL database:**
```bash
python data/init_db.py
```

This will create:
- `emergency_dispatch` database
- `cases` table (stores AI analysis results)
- `feedback` table (stores operator corrections for RLHF)
- Necessary indexes for performance

5. **Test database connection:**
```bash
python test_db_connection.py
```

6. **Run server:**
```bash
python main.py
```

## API Endpoints

### Audio Analysis
- **POST** `/api/analyze-audio` - Analyze emergency audio file

### Cases (Full CRUD)
- **GET** `/api/case/{case_id}` - Retrieve a specific case by ID
- **GET** `/api/cases?limit=100&offset=0` - Retrieve all cases (paginated)
- **PUT** `/api/case/{case_id}` - Update a case's information
- **DELETE** `/api/case/{case_id}` - Delete a case (⚠️ also deletes feedback)
- **GET** `/api/get-case/{case_id}` - [DEPRECATED] Use `/api/case/{case_id}` instead

### Feedback (Full CRUD + Upsert)
- **POST** `/api/operator-feedback` - Submit/Update operator corrections (UPSERT)
- **GET** `/api/feedback/{feedback_id}` - Retrieve a specific feedback by ID
- **GET** `/api/feedbacks?limit=100&offset=0` - Retrieve all feedbacks (paginated)
- **PUT** `/api/feedback/{feedback_id}` - Update feedback information
- **DELETE** `/api/feedback/{feedback_id}` - Delete feedback only

**Note:** Each case can have only ONE feedback (one-to-one relationship)

### Analytics
- **GET** `/api/analytics` - Retrieve comprehensive dashboard analytics
  - Feedback analysis (edited vs correct cases, edit/acceptance rates)
  - Average confidence scores (incident, severity, dispatch)
  - Incident types distribution with counts and percentages
  - Language distribution (en, ar, etc.)
  - Severity levels distribution (CRITICAL, HIGH, MEDIUM, LOW)
  - Dispatch units distribution (AMBULANCE, POLICE, FIRE_DEPARTMENT, etc.)

### Model Training
- **POST** `/api/retrain-model` - Trigger RLHF training

### System
- **GET** `/api/health` - Health check

## Architecture

```
Audio → STT → Language Detection → Incident → Severity → Dispatch → Evaluation → PostgreSQL
```

**Database Schema:**
- `cases` table: Stores transcripts, AI predictions, confidence scores
- `feedback` table: Stores operator corrections (linked via foreign key)
- Indexes: Optimized for recent cases, review queue, and feedback queries

## Database

This project uses **PostgreSQL 15** for persistent storage.

**Key Features:**
- ACID compliance for data integrity
- Foreign key constraints between cases and feedback
- Optimized indexes for common queries
- Connection pooling for performance
- Automatic timestamps

**Database Configuration:**
- Connection settings in `config/config.yaml`
- Environment variables in `.env`
- Initialization script: `data/init_db.py`
- Test script: `test_db_connection.py`

**Common Operations:**
```bash
# Initialize database
python data/init_db.py

# Test connection
python test_db_connection.py

# Backup database
pg_dump -U postgres emergency_dispatch > backup.sql

# Restore database
psql -U postgres emergency_dispatch < backup.sql
```

For detailed database documentation, see `INSTALLATION_GUIDE.md`.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Test database connection
python test_db_connection.py

# Test API endpoints
./test_api.sh
```

## Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Installation Guide**: `INSTALLATION_GUIDE.md` (detailed setup instructions)
- **Quick Start**: `QUICK_START.md` (1-minute setup)
- **Project Structure**: `PROJECT_STRUCTURE.md` (architecture overview)

## Configuration Files

- `.env` - Environment variables (database, API keys)
- `config/config.yaml` - Application configuration
- `docker-compose.yml` - Docker services setup
- `requirements.txt` - Python dependencies

## Troubleshooting

### Database Connection Issues
1. Ensure PostgreSQL is running: `sudo systemctl status postgresql`
2. Check credentials in `.env` match your PostgreSQL setup
3. Run `python test_db_connection.py` for diagnostics

### Import Errors
```bash
pip install -r requirements.txt --upgrade
```

See `INSTALLATION_GUIDE.md` for detailed troubleshooting.

## License

MIT

