# AI Emergency Dispatch Assistant

A production-ready multilingual multi-agent AI system for emergency 911 call analysis with real-time streaming support.

## Features

| Feature | Description |
|---------|-------------|
| Multilingual Support | Arabic + English with auto-detection |
| Speech-to-Text | OpenAI Whisper API integration |
| Incident Classification | AI-powered emergency type detection |
| Severity Assessment | Urgency level evaluation |
| Dispatch Recommendation | Smart unit allocation |
| Real-time Streaming | WebSocket audio processing |
| Human-in-the-Loop | Operator review and correction |
| Mini-RLHF | Continuous model improvement |

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-key

# Start all services
docker-compose up -d
```

Access the API at http://localhost:8000

### Option 2: Local Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 3. Initialize database
python data/init_db.py

# 4. Run the server
python main.py
```

### Frontend Development

```bash
cd view
npm install
npm run dev
```

Access the UI at http://localhost:5173

---

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze-audio` | Analyze audio file |
| GET | `/api/case/{id}` | Get case by ID |
| GET | `/api/cases` | List all cases |
| POST | `/api/operator-feedback` | Submit correction |
| GET | `/api/analytics` | Dashboard analytics |
| GET | `/api/health` | Health check |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://localhost:8000/ws/audio` | Real-time audio streaming |

### Interactive Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Architecture

```
Audio Input --> STT --> Language Detection --> Incident --> Severity --> Dispatch --> Evaluation --> Database
                                                     |
                                                     v
                                              Human Review
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture & design |
| [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | Database tables & queries |
| [FRONTEND_GUIDE.md](docs/FRONTEND_GUIDE.md) | Frontend development guide |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md) | Detailed setup instructions |
| [API_EXAMPLES.md](docs/API_EXAMPLES.md) | API usage examples |
| [WEBSOCKET_STREAMING.md](docs/WEBSOCKET_STREAMING.md) | WebSocket implementation |

---

## Project Structure

```
.dev/
├── agents/         # AI agent implementations
├── api/            # FastAPI routers
├── config/         # Configuration files
├── controllers/    # Business logic
├── data/           # Database scripts
├── docs/           # Documentation
├── graph/          # LangGraph workflows
├── models/         # ML model wrappers
├── services/       # Specialized services
├── tests/          # Test suites
├── view/           # React frontend
├── main.py         # Application entry
└── docker-compose.yml
```

---

## Configuration

### Environment Variables (`.env`)

```bash
OPENAI_API_KEY=your-key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=emergency_dispatch
DB_USER=postgres
DB_PASSWORD=postgres
```

### Application Config (`config/config.yaml`)

See the file for full configuration options including:
- App settings (host, port)
- Database connection
- Model parameters
- Streaming settings
- Logging configuration

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Test database connection
python tests/test_db_connection.py

# Test API endpoints
./scripts/test_api.sh
```

---

## Tech Stack

### Backend
- **FastAPI** - Web framework
- **LangGraph** - Agent orchestration
- **LangChain** - LLM integration
- **OpenAI Whisper** - Speech-to-text
- **PostgreSQL** - Database

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Development setup
- Coding standards
- Git workflow
- Testing requirements
- Code review process

---

## Troubleshooting

### Database Issues
```bash
# Test connection
python tests/test_db_connection.py

# Reinitialize database
python data/init_db.py
```

### Import Errors
```bash
pip install -r requirements.txt --upgrade
```

### Frontend Issues
```bash
cd view
rm -rf node_modules
npm install
```

See [docs/DATABASE_TROUBLESHOOTING.md](docs/DATABASE_TROUBLESHOOTING.md) for more help.

---

## License

MIT
