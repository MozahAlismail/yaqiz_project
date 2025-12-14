# Contributing Guide

Welcome to the AI Emergency Dispatch Assistant project! This guide will help you contribute effectively to the codebase.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Coding Standards](#coding-standards)
5. [Git Workflow](#git-workflow)
6. [Testing](#testing)
7. [Documentation](#documentation)
8. [Code Review](#code-review)

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 15
- Git

### Quick Setup

```bash
# Clone the repository
git clone <repository-url>
cd .dev

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
cp .env.example .env
# Edit .env with your credentials
python data/init_db.py

# Frontend setup
cd view
npm install
cd ..

# Start development
python main.py          # Backend on :8000
cd view && npm run dev  # Frontend on :5173
```

---

## Development Setup

### Environment Variables

Create `.env` in project root:

```bash
# API Keys
OPENAI_API_KEY=your-openai-key

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=emergency_dispatch
DB_USER=postgres
DB_PASSWORD=postgres
```

### IDE Setup

**VSCode Extensions (Recommended):**
- Python
- Pylance
- ESLint
- Tailwind CSS IntelliSense
- TypeScript Toolbox

**Settings:**
```json
{
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "typescript.preferences.importModuleSpecifier": "relative"
}
```

---

## Project Structure

```
.dev/
├── agents/         # AI agents (language, incident, severity, dispatch)
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
└── main.py         # Application entry point
```

See `docs/ARCHITECTURE.md` for detailed architecture documentation.

---

## Coding Standards

### Python

**Style:**
- Follow PEP 8
- Use Black formatter
- Maximum line length: 100 characters

**Naming:**
```python
# Classes: PascalCase
class IncidentClassifier:
    pass

# Functions/methods: snake_case
def classify_incident(transcript: str) -> dict:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private: leading underscore
def _internal_helper():
    pass
```

**Type Hints:**
```python
from typing import Optional, List, Dict

def process_audio(
    audio_path: str,
    language: Optional[str] = None
) -> Dict[str, any]:
    ...
```

**Docstrings:**
```python
def analyze_transcript(transcript: str, language: str) -> dict:
    """
    Analyze emergency call transcript.

    Args:
        transcript: Full text of the call
        language: Language code (en or ar)

    Returns:
        Dictionary with incident_type, severity, dispatch_unit

    Raises:
        ValueError: If transcript is empty
    """
    ...
```

### TypeScript/React

**Style:**
- Use ESLint config
- Use Prettier for formatting

**Naming:**
```typescript
// Components: PascalCase
const AudioPlayer: React.FC<Props> = () => {};

// Functions: camelCase
function formatTimestamp(date: Date): string {}

// Types/Interfaces: PascalCase
interface AudioPlayerProps {
  isPlaying: boolean;
  onPlay: () => void;
}

// Constants: UPPER_SNAKE_CASE
const MAX_VOLUME = 100;
```

**Component Structure:**
```typescript
// 1. Imports
import React from 'react';
import { useTimer } from '../hooks';

// 2. Types
interface Props {
  label: string;
  onClick?: () => void;
}

// 3. Component
export const Button: React.FC<Props> = ({ label, onClick }) => {
  // Hooks
  const [isActive, setIsActive] = useState(false);

  // Handlers
  const handleClick = () => {
    setIsActive(true);
    onClick?.();
  };

  // Render
  return <button onClick={handleClick}>{label}</button>;
};
```

---

## Git Workflow

### Branch Naming

```
feature/add-audio-player
bugfix/fix-transcription-error
hotfix/security-patch
refactor/cleanup-api-routes
docs/update-readme
```

### Commit Messages

Follow conventional commits:

```
feat: add real-time audio streaming
fix: resolve memory leak in WebSocket handler
docs: update API documentation
refactor: simplify incident classification logic
test: add unit tests for severity classifier
chore: update dependencies
```

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Example:**
```
feat(audio): add volume control slider

- Add Slider component for volume adjustment
- Integrate with AudioPlayer
- Store volume preference in localStorage

Closes #123
```

### Pull Request Process

1. **Create branch** from `main`
2. **Make changes** following coding standards
3. **Write/update tests**
4. **Update documentation** if needed
5. **Create PR** with description
6. **Request review** from team member
7. **Address feedback**
8. **Merge** after approval

### PR Template

```markdown
## Summary
Brief description of changes

## Changes
- Added X
- Fixed Y
- Updated Z

## Testing
How to test these changes

## Screenshots
(if UI changes)

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No console errors/warnings
```

---

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py

# Run specific test
pytest tests/unit/test_agents.py::test_incident_classification
```

**Test Structure:**
```python
# tests/unit/test_incident_classifier.py

import pytest
from models.incident_classifier import IncidentClassifier

class TestIncidentClassifier:
    @pytest.fixture
    def classifier(self):
        return IncidentClassifier(config={})

    def test_classify_medical_emergency(self, classifier):
        result = classifier.classify("Someone is having a heart attack")
        assert result["incident_type"] == "MEDICAL"

    def test_classify_empty_transcript(self, classifier):
        with pytest.raises(ValueError):
            classifier.classify("")
```

### Frontend Tests

```bash
cd view

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

---

## Documentation

### Where to Document

| What | Where |
|------|-------|
| API endpoints | `docs/API_EXAMPLES.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Database | `docs/DATABASE_SCHEMA.md` |
| Frontend | `docs/FRONTEND_GUIDE.md` |
| Setup | `README.md`, `docs/INSTALLATION_GUIDE.md` |

### Documentation Standards

- Use Markdown
- Include code examples
- Keep up-to-date with code changes
- Add diagrams where helpful

---

## Code Review

### For Authors

- Keep PRs focused and small
- Explain the "why" in PR description
- Respond to feedback promptly
- Don't take feedback personally

### For Reviewers

- Be constructive and specific
- Approve if changes are acceptable
- Use suggestions for minor fixes
- Block only for significant issues

### Review Checklist

- [ ] Code follows standards
- [ ] Logic is correct
- [ ] Error handling is appropriate
- [ ] Tests cover changes
- [ ] Documentation updated
- [ ] No security issues
- [ ] Performance considered

---

## Common Tasks

### Adding a New API Endpoint

1. Create router in `api/new_router.py`
2. Add business logic in `controllers/`
3. Include router in `main.py`
4. Add tests in `tests/`
5. Document in `docs/API_EXAMPLES.md`

### Adding a New Agent

1. Create model in `models/`
2. Create agent in `agents/`
3. Add node in `graph/nodes.py`
4. Update workflow in `graph/workflow.py`
5. Initialize in `main.py`
6. Add tests

### Adding a New Frontend Component

1. Create in `view/shared/components/`
2. Export from `index.ts`
3. Add TypeScript types
4. Add to storybook (if available)
5. Document usage

---

## Getting Help

- Check existing documentation in `docs/`
- Search existing issues
- Ask in team chat
- Create an issue with `[Question]` prefix

---

## License

This project is licensed under MIT. See LICENSE file for details.
