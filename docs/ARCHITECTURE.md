# Architecture Documentation

## System Overview

The AI Emergency Dispatch Assistant is a production-ready multilingual multi-agent AI system designed to analyze emergency 911 calls in real-time. The system processes audio calls, transcribes them, detects languages (Arabic & English), classifies incident types, assesses severity, recommends dispatch units, and includes human-in-the-loop review capabilities.

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI 0.115+ | REST API framework |
| LangGraph 0.2.0+ | AI agent orchestration & workflow management |
| LangChain | LLM integration (GPT-4 Turbo, GPT-4o-mini) |
| OpenAI Whisper API | Speech-to-Text transcription |
| PostgreSQL 15 | Primary database |
| asyncpg/psycopg2 | Database drivers |
| Uvicorn | ASGI server |
| Loguru | Structured logging |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18.3.1 | UI framework |
| TypeScript 5.7.2 | Type-safe JavaScript |
| Vite 6.0.3 | Build tool & dev server |
| Tailwind CSS 3.4.15 | Utility-first CSS |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |

---

## High-Level Architecture

```
                                   +------------------+
                                   |   React Frontend |
                                   |   (Vite + TS)    |
                                   +--------+---------+
                                            |
                                            | HTTP/WebSocket
                                            v
+------------------+              +------------------+              +------------------+
|   Audio Input    | ----------> |   FastAPI        | ----------> |   PostgreSQL     |
|   (Microphone/   |   WebSocket |   Application    |   asyncpg   |   Database       |
|    Audio File)   |             |                  |             |                  |
+------------------+             +--------+---------+             +------------------+
                                          |
                                          | LangGraph
                                          v
                        +----------------------------------+
                        |       AI Agent Pipeline          |
                        |                                  |
                        |  STT -> Language -> Incident ->  |
                        |  Severity -> Dispatch -> Eval    |
                        +----------------------------------+
```

---

## Directory Structure

```
.dev/
├── agents/                 # AI agent implementations
│   ├── language_detection_agent.py
│   ├── incident_agent.py
│   ├── severity_agent.py
│   ├── dispatch_agent.py
│   └── self_eval_agent.py
│
├── api/                    # REST API routers
│   ├── audio_router.py            # Audio file analysis
│   ├── feedback_router.py         # Operator feedback
│   ├── case_router.py             # Case CRUD
│   ├── analytics_router.py        # Dashboard analytics
│   ├── retrain_router.py          # RLHF training trigger
│   ├── health_router.py           # Health checks
│   ├── realtime_audio_router.py   # Real-time audio
│   ├── websocket_audio_router.py  # WebSocket streaming
│   └── streaming_review_router.py # Review queue
│
├── config/                 # Configuration files
│   ├── config.yaml                # Main app config
│   ├── emergency_rules/           # Classification rules
│   │   ├── en/                    # English rules
│   │   └── ar/                    # Arabic rules
│   └── prompts/                   # LLM prompt templates
│
├── controllers/            # Business logic layer
│   ├── agent_controller.py
│   ├── main_controller.py
│   ├── realtime_audio_controller.py
│   └── streaming_case_controller.py
│
├── data/                   # Database management
│   ├── init_db.py                 # Schema initialization
│   └── migrate_*.py               # Migration scripts
│
├── docs/                   # Documentation
│
├── graph/                  # LangGraph workflows
│   ├── state.py                   # Batch workflow state
│   ├── streaming_state.py         # Streaming workflow state
│   ├── nodes.py                   # Graph nodes (processing steps)
│   ├── streaming_nodes.py         # Streaming-specific nodes
│   ├── edges.py                   # Routing logic
│   ├── streaming_edges.py         # Streaming routing
│   ├── workflow.py                # Batch workflow
│   ├── streaming_workflow.py      # Real-time streaming workflow
│   └── audio_analysis_workflow.py # Audio file workflow
│
├── models/                 # ML model wrappers
│   ├── language_model.py          # Language detection
│   ├── stt_model.py               # Speech-to-Text
│   ├── incident_classifier.py    # Incident classification
│   ├── severity_classifier.py    # Severity assessment
│   ├── dispatch_classifier.py    # Dispatch recommendation
│   ├── translation_model.py      # Translation
│   └── rlhf_trainer.py            # RLHF training
│
├── services/               # Specialized services
│   ├── realtime_audio_service.py
│   ├── websocket_audio_service.py
│   └── streaming_graph_service.py
│
├── tests/                  # Test suites
│   ├── unit/
│   └── integration/
│
├── view/                   # React frontend
│   └── src/
│       ├── components/
│       ├── context/
│       ├── hooks/
│       ├── services/
│       └── shared/
│
├── main.py                 # Application entry point
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Workflow Architecture

### Batch Processing Workflow
For processing audio files uploaded via REST API:

```
┌─────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  Audio File │ --> │  STT (Whisper)   │ --> │ Language Detection │
└─────────────┘     └──────────────────┘     └─────────┬──────────┘
                                                       │
                                                       v
┌─────────────────┐     ┌────────────────────┐     ┌───────────────────┐
│ Self-Evaluation │ <-- │ Dispatch Selection │ <-- │ Severity Classify │
└────────┬────────┘     └────────────────────┘     └───────────────────┘
         │                                                    ^
         │                                                    │
         v                                         ┌──────────┴──────────┐
┌─────────────────┐                                │ Incident Classify   │
│   PostgreSQL    │                                └─────────────────────┘
└─────────────────┘
```

### Streaming Workflow
For real-time microphone audio processing:

```
┌────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  WebSocket     │ --> │  Whisper STT     │ --> │ Incident Classify   │
│  Audio Chunks  │     │  (Real-time)     │     │                     │
└────────────────┘     └──────────────────┘     └──────────┬──────────┘
                                                           │
                                                           v
┌───────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Confidence Gate   │ <-- │ Dispatch Classify │ <-- │ Severity Classify │
└────────┬──────────┘     └──────────────────┘     └──────────────────┘
         │
         ├── Continue (wait for more audio)
         │
         └── Exit (confidence met / timeout / critical)
                    │
                    v
            ┌──────────────────┐
            │ Human Review     │
            │ Queue            │
            └──────────────────┘
```

---

## Component Details

### 1. Agents (`agents/`)
Each agent wraps a model and provides a consistent interface:

| Agent | Purpose | Model |
|-------|---------|-------|
| `LanguageDetectionAgent` | Detect ar/en language | langdetect library |
| `IncidentAgent` | Classify incident type | GPT-4o-mini |
| `SeverityAgent` | Assess severity level | GPT-4o-mini |
| `DispatchAgent` | Recommend dispatch unit | GPT-4o-mini |
| `SelfEvaluationAgent` | Quality assessment | GPT-4o-mini |

### 2. Models (`models/`)
Low-level ML model implementations:

| Model | Purpose | Implementation |
|-------|---------|----------------|
| `stt_model.py` | Speech-to-Text | OpenAI Whisper API |
| `language_model.py` | Language detection | langdetect |
| `incident_classifier.py` | Incident classification | LangChain + GPT |
| `severity_classifier.py` | Severity assessment | LangChain + GPT |
| `dispatch_classifier.py` | Dispatch recommendation | LangChain + GPT |
| `translation_model.py` | Arabic/English translation | GPT-4o-mini |
| `rlhf_trainer.py` | Feedback-based training | Custom RLHF |

### 3. Graph Workflows (`graph/`)
LangGraph-based workflow orchestration:

| Workflow | File | Purpose |
|----------|------|---------|
| Batch | `workflow.py` | Process audio files |
| Streaming | `streaming_workflow.py` | Real-time audio |
| Audio Analysis | `audio_analysis_workflow.py` | File-based STT pipeline |

### 4. API Layer (`api/`)
FastAPI routers for all endpoints:

| Router | Endpoints | Purpose |
|--------|-----------|---------|
| `audio_router` | POST /api/analyze-audio | Analyze audio files |
| `case_router` | GET/PUT/DELETE /api/case/* | Case CRUD |
| `feedback_router` | POST /api/operator-feedback | Submit corrections |
| `analytics_router` | GET /api/analytics | Dashboard data |
| `websocket_audio_router` | WS /ws/audio | Real-time streaming |
| `streaming_review_router` | GET /api/streaming-review/* | Review queue |

### 5. Services (`services/`)
Specialized business logic:

| Service | Purpose |
|---------|---------|
| `realtime_audio_service.py` | Audio chunk processing |
| `websocket_audio_service.py` | WebSocket connection management |
| `streaming_graph_service.py` | Streaming workflow orchestration |

---

## Data Flow

### 1. Audio File Analysis
```
1. Client uploads audio file to POST /api/analyze-audio
2. STT model transcribes audio to text
3. Language detection identifies ar/en
4. Incident classifier categorizes emergency type
5. Severity classifier assesses urgency
6. Dispatch classifier recommends units
7. Self-evaluation scores confidence
8. Results saved to PostgreSQL
9. Response returned to client
```

### 2. Real-time Streaming
```
1. Client connects to WebSocket /ws/audio
2. Audio chunks sent every 100ms
3. Whisper processes chunks incrementally
4. Classification runs on accumulated transcript
5. Confidence gate evaluates:
   - If confidence >= threshold: complete
   - If severity == CRITICAL: complete
   - If timeout (10s): complete
   - Otherwise: continue
6. Completed cases go to human review queue
```

---

## Configuration

### Main Config (`config/config.yaml`)
```yaml
app:
  host: "0.0.0.0"
  port: 8000

database:
  host: localhost
  port: 5432
  database: emergency_dispatch
  user: postgres
  password: postgres

streaming:
  confidence_threshold: 0.75
  evaluation_window_seconds: 10.0

hitl:
  enabled: true
  confidence_threshold: 0.75

logging:
  level: INFO
  log_file: logs/app.log
```

### Environment Variables (`.env`)
```bash
OPENAI_API_KEY=your-key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=emergency_dispatch
DB_USER=postgres
DB_PASSWORD=postgres
```

---

## Key Design Decisions

### 1. LangGraph for Orchestration
- Provides state machine semantics
- Enables checkpointing for HITL workflows
- Allows conditional routing between agents
- Supports both batch and streaming modes

### 2. Separate Streaming Workflow
- Streaming has different timing requirements
- Confidence gate enables early exit
- Time-bounded evaluation (10s window)
- All cases require human review

### 3. PostgreSQL over SQLite
- Production-ready database
- ACID compliance for data integrity
- Foreign key constraints
- Better concurrency support

### 4. WebSocket for Audio
- Low latency audio streaming
- Bidirectional communication
- Real-time status updates
- Efficient for continuous audio

---

## Extending the System

### Adding a New Agent
1. Create model in `models/new_model.py`
2. Create agent in `agents/new_agent.py`
3. Add node in `graph/nodes.py`
4. Update workflow in `graph/workflow.py`
5. Initialize in `main.py`

### Adding a New API Endpoint
1. Create router in `api/new_router.py`
2. Add business logic to controllers
3. Include router in `main.py`
4. Update documentation

### Adding a New Language
1. Add rules in `config/emergency_rules/{lang}/`
2. Update language detection model
3. Add translation support if needed
4. Update prompts for the new language

---

## Performance Considerations

- **Connection Pooling**: asyncpg for database connections
- **Async I/O**: All endpoints are async
- **Checkpointing**: MemorySaver for workflow state
- **Streaming**: Chunked audio processing
- **Caching**: Model instances initialized once at startup
