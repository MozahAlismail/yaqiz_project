# Project Structure

## Overview

This document provides a complete overview of the AI Emergency Dispatch Assistant project structure.

## Directory Tree

```
.dev/
├── agents/                         # AI Agent Implementations
│   ├── __init__.py
│   ├── language_detection_agent.py # Language detection (ar/en)
│   ├── incident_agent.py           # Incident type classification
│   ├── severity_agent.py           # Severity level assessment
│   ├── dispatch_agent.py           # Dispatch unit recommendation
│   └── self_eval_agent.py          # Quality self-evaluation
│
├── api/                            # FastAPI Routers
│   ├── __init__.py
│   ├── audio_router.py             # POST /api/analyze-audio
│   ├── case_router.py              # CRUD /api/case/*
│   ├── feedback_router.py          # POST /api/operator-feedback
│   ├── analytics_router.py         # GET /api/analytics
│   ├── retrain_router.py           # POST /api/retrain-model
│   ├── health_router.py            # GET /api/health
│   ├── realtime_audio_router.py    # Real-time audio processing
│   ├── websocket_audio_router.py   # WS /ws/audio
│   └── streaming_review_router.py  # Streaming review queue
│
├── config/                         # Configuration
│   ├── config.yaml                 # Main application config
│   ├── prompts/                    # LLM Prompt Templates
│   │   ├── incident_prompt.txt
│   │   ├── severity_prompt.txt
│   │   ├── dispatch_prompt.txt
│   │   ├── evaluation_prompt.txt
│   │   └── translation_prompt.txt
│   └── emergency_rules/            # Classification Rules
│       ├── en/                     # English rules
│       │   ├── incident_rules.json
│       │   ├── severity_rules.json
│       │   ├── dispatch_rules.json
│       │   └── evaluation_rules.json
│       └── ar/                     # Arabic rules
│           ├── incident_rules.json
│           ├── severity_rules.json
│           ├── dispatch_rules.json
│           └── evaluation_rules.json
│
├── controllers/                    # Business Logic Layer
│   ├── __init__.py
│   ├── agent_controller.py         # Agent orchestration
│   ├── main_controller.py          # Main business logic
│   ├── realtime_audio_controller.py
│   └── streaming_case_controller.py
│
├── data/                           # Database Management
│   ├── init_db.py                  # Database initialization
│   ├── migrate_add_unique_constraint.py
│   └── migrate_streaming_columns.py
│
├── docs/                           # Documentation
│   ├── README.md
│   ├── QUICK_START.md
│   ├── INSTALLATION_GUIDE.md
│   ├── PROJECT_STRUCTURE.md        # This file
│   ├── ARCHITECTURE.md             # System architecture
│   ├── DATABASE_SCHEMA.md          # Database documentation
│   ├── FRONTEND_GUIDE.md           # Frontend development guide
│   ├── API_EXAMPLES.md
│   ├── ANALYTICS.md
│   ├── CRUD_OPERATIONS.md
│   ├── DATABASE_TROUBLESHOOTING.md
│   ├── REALTIME_AUDIO_WORKFLOW.md
│   ├── WEBSOCKET_STREAMING.md
│   ├── WEBSOCKET_IMPLEMENTATION_SUMMARY.md
│   └── WORKFLOW_DIAGRAM.md
│
├── graph/                          # LangGraph Workflows
│   ├── state.py                    # Batch workflow state schema
│   ├── streaming_state.py          # Streaming workflow state
│   ├── nodes.py                    # Graph nodes (processing steps)
│   ├── streaming_nodes.py          # Streaming-specific nodes
│   ├── edges.py                    # Routing logic
│   ├── streaming_edges.py          # Streaming routing
│   ├── workflow.py                 # Main batch workflow
│   ├── streaming_workflow.py       # Real-time streaming workflow
│   └── audio_analysis_workflow.py  # Audio file analysis workflow
│
├── models/                         # ML Model Wrappers
│   ├── __init__.py
│   ├── stt_model.py                # Speech-to-Text (OpenAI Whisper)
│   ├── language_model.py           # Language detection
│   ├── incident_classifier.py      # Incident classification
│   ├── severity_classifier.py      # Severity assessment
│   ├── dispatch_classifier.py      # Dispatch recommendation
│   ├── translation_model.py        # Arabic/English translation
│   └── rlhf_trainer.py             # Mini-RLHF training
│
├── scripts/                        # Utility Scripts
│   ├── run.sh                      # Startup script
│   └── test_api.sh                 # API testing script
│
├── services/                       # Specialized Services
│   ├── realtime_audio_service.py
│   ├── websocket_audio_service.py
│   └── streaming_graph_service.py
│
├── static/                         # Static Assets
│   └── dashboard.html              # Analytics dashboard
│
├── tests/                          # Test Suites
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_db_connection.py       # Database tests
│   ├── test_microphone_client.py
│   ├── test_websocket_client.py
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_language_model.py
│   │   ├── test_agents.py
│   │   └── test_database.py
│   └── integration/                # Integration tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_pipeline.py
│
├── view/                           # React Frontend
│   ├── src/
│   │   ├── App.tsx                 # Main application
│   │   ├── main.tsx                # Entry point
│   │   ├── components/             # Core components
│   │   │   ├── ErrorBoundary.tsx
│   │   │   └── Layout.tsx
│   │   ├── context/                # React contexts
│   │   │   ├── LanguageContext.tsx
│   │   │   └── ThemeContext.tsx
│   │   ├── hooks/                  # Custom hooks
│   │   └── services/               # API services
│   │
│   ├── realtime_incident/          # Real-time call view
│   │   ├── RealtimeIncidentView.tsx
│   │   └── components/
│   │
│   ├── accepted_incident/          # Reviewed incident view
│   │   ├── AcceptedIncidentView.tsx
│   │   └── components/
│   │
│   ├── incidents_list/             # Incident list view
│   │   ├── IncidentsListView.tsx
│   │   └── components/
│   │
│   ├── shared/                     # Shared components
│   │   ├── components/             # Reusable UI components
│   │   ├── hooks/                  # Shared hooks
│   │   ├── icons/                  # Icon components
│   │   └── types/                  # TypeScript types
│   │
│   ├── i18n/                       # Internationalization
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── audio/                          # Sample Audio Files
│   └── emergency.wav
│
├── logs/                           # Application Logs (runtime)
│
├── main.py                         # Application Entry Point
├── requirements.txt                # Python Dependencies
├── requirements-pinned.txt         # Pinned Dependencies
├── Dockerfile                      # Docker Container Definition
├── docker-compose.yml              # Docker Compose Config
├── .env.example                    # Environment Template
├── .gitignore                      # Git Ignore Patterns
├── CONTRIBUTING.md                 # Contribution Guidelines
└── README.md                       # Project Documentation
```

## Component Summary

### Backend Components

| Directory | Files | Purpose |
|-----------|-------|---------|
| `agents/` | 5 | AI agent implementations |
| `api/` | 9 | REST API endpoints |
| `controllers/` | 4 | Business logic |
| `data/` | 3 | Database management |
| `graph/` | 9 | LangGraph workflows |
| `models/` | 7 | ML model wrappers |
| `services/` | 3 | Specialized services |

### Frontend Components

| Directory | Files | Purpose |
|-----------|-------|---------|
| `view/src/` | 6 | Core React app |
| `view/realtime_incident/` | 12 | Real-time call handling |
| `view/accepted_incident/` | ~10 | Reviewed incidents |
| `view/incidents_list/` | ~10 | Incident dashboard |
| `view/shared/` | 30+ | Reusable components |

### Configuration

| File | Purpose |
|------|---------|
| `config/config.yaml` | Main application settings |
| `config/prompts/*.txt` | LLM prompt templates |
| `config/emergency_rules/` | Classification rule JSONs |
| `.env` | Environment variables |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `CONTRIBUTING.md` | Contribution guidelines |
| `docs/ARCHITECTURE.md` | System architecture |
| `docs/DATABASE_SCHEMA.md` | Database documentation |
| `docs/FRONTEND_GUIDE.md` | Frontend development |
| `docs/API_EXAMPLES.md` | API usage examples |

## Key Files

### Entry Points

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry |
| `view/src/main.tsx` | React application entry |

### Configuration

| File | Purpose |
|------|---------|
| `config/config.yaml` | Application configuration |
| `vite.config.ts` | Frontend build configuration |
| `docker-compose.yml` | Container orchestration |

### Database

| File | Purpose |
|------|---------|
| `data/init_db.py` | Database schema initialization |
| `data/migrate_*.py` | Database migrations |

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Database tables and queries
- [FRONTEND_GUIDE.md](FRONTEND_GUIDE.md) - Frontend development guide
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
