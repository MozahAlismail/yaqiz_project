# Database Schema Documentation

## Overview

The AI Emergency Dispatch Assistant uses PostgreSQL 15 as its primary database. The schema is designed to store emergency case data, AI predictions, and operator feedback for continuous improvement.

## Database: `emergency_dispatch`

## Tables

### 1. `cases` Table

Stores all emergency call cases with AI analysis results.

```sql
CREATE TABLE cases (
    case_id VARCHAR(36) PRIMARY KEY,
    transcript TEXT NOT NULL,
    detected_language VARCHAR(10),
    language_confidence REAL,
    ai_incident VARCHAR(100),
    ai_severity VARCHAR(50),
    ai_unit VARCHAR(100),
    incident_confidence REAL,
    severity_confidence REAL,
    dispatch_confidence REAL,
    requires_review BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `case_id` | VARCHAR(36) | NO | Primary key, UUID format |
| `transcript` | TEXT | NO | Full transcription of the call |
| `detected_language` | VARCHAR(10) | YES | Language code (en, ar) |
| `language_confidence` | REAL | YES | Language detection confidence (0.0-1.0) |
| `ai_incident` | VARCHAR(100) | YES | AI-predicted incident type |
| `ai_severity` | VARCHAR(50) | YES | AI-predicted severity level |
| `ai_unit` | VARCHAR(100) | YES | AI-recommended dispatch unit |
| `incident_confidence` | REAL | YES | Incident classification confidence |
| `severity_confidence` | REAL | YES | Severity assessment confidence |
| `dispatch_confidence` | REAL | YES | Dispatch recommendation confidence |
| `requires_review` | BOOLEAN | YES | Flag for human review queue |
| `created_at` | TIMESTAMP | YES | Auto-generated timestamp |

**Indexes:**
```sql
-- For fetching recent cases
CREATE INDEX idx_cases_created_at ON cases(created_at DESC);

-- For fetching cases requiring review
CREATE INDEX idx_cases_requires_review ON cases(requires_review)
    WHERE requires_review = TRUE;
```

---

### 2. `feedback` Table

Stores operator corrections for RLHF training.

```sql
CREATE TABLE feedback (
    feedback_id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL UNIQUE,
    corrected_incident VARCHAR(100),
    corrected_severity VARCHAR(50),
    corrected_unit VARCHAR(100),
    operator_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
);
```

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `feedback_id` | VARCHAR(36) | NO | Primary key, UUID format |
| `case_id` | VARCHAR(36) | NO | Foreign key to cases (UNIQUE - one feedback per case) |
| `corrected_incident` | VARCHAR(100) | YES | Operator-corrected incident type |
| `corrected_severity` | VARCHAR(50) | YES | Operator-corrected severity |
| `corrected_unit` | VARCHAR(100) | YES | Operator-corrected dispatch unit |
| `operator_id` | VARCHAR(100) | YES | ID of the reviewing operator |
| `timestamp` | TIMESTAMP | YES | When feedback was submitted |

**Indexes:**
```sql
-- For joining with cases
CREATE INDEX idx_feedback_case_id ON feedback(case_id);

-- For fetching recent feedback
CREATE INDEX idx_feedback_timestamp ON feedback(timestamp DESC);
```

---

## Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                          cases                                │
├──────────────────────────────────────────────────────────────┤
│ case_id (PK)           VARCHAR(36)                           │
│ transcript             TEXT                                   │
│ detected_language      VARCHAR(10)                           │
│ language_confidence    REAL                                  │
│ ai_incident            VARCHAR(100)                          │
│ ai_severity            VARCHAR(50)                           │
│ ai_unit                VARCHAR(100)                          │
│ incident_confidence    REAL                                  │
│ severity_confidence    REAL                                  │
│ dispatch_confidence    REAL                                  │
│ requires_review        BOOLEAN                               │
│ created_at             TIMESTAMP                             │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             │ 1:1 (ON DELETE CASCADE)
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                         feedback                              │
├──────────────────────────────────────────────────────────────┤
│ feedback_id (PK)       VARCHAR(36)                           │
│ case_id (FK, UNIQUE)   VARCHAR(36)                           │
│ corrected_incident     VARCHAR(100)                          │
│ corrected_severity     VARCHAR(50)                           │
│ corrected_unit         VARCHAR(100)                          │
│ operator_id            VARCHAR(100)                          │
│ timestamp              TIMESTAMP                             │
└──────────────────────────────────────────────────────────────┘
```

---

## Enumerated Values

### Incident Types (`ai_incident`, `corrected_incident`)
- `MEDICAL` - Medical emergency
- `FIRE` - Fire-related incident
- `POLICE` - Police/Crime-related
- `TRAFFIC` - Traffic accident
- `OTHER` - Unclassified

### Severity Levels (`ai_severity`, `corrected_severity`)
- `CRITICAL` - Immediate response required
- `HIGH` - Urgent response needed
- `MEDIUM` - Standard response
- `LOW` - Non-urgent

### Dispatch Units (`ai_unit`, `corrected_unit`)
- `AMBULANCE` - Medical emergency
- `FIRE_DEPARTMENT` - Fire response
- `POLICE` - Law enforcement
- `MULTIPLE` - Multiple units needed

### Languages (`detected_language`)
- `en` - English
- `ar` - Arabic

---

## Common Queries

### Get all cases requiring review
```sql
SELECT * FROM cases
WHERE requires_review = TRUE
ORDER BY created_at DESC;
```

### Get case with feedback
```sql
SELECT c.*, f.corrected_incident, f.corrected_severity, f.corrected_unit
FROM cases c
LEFT JOIN feedback f ON c.case_id = f.case_id
WHERE c.case_id = 'your-case-id';
```

### Get analytics data
```sql
-- Incident distribution
SELECT ai_incident, COUNT(*) as count
FROM cases
GROUP BY ai_incident;

-- Cases corrected by operators
SELECT
    COUNT(*) as total_cases,
    COUNT(f.feedback_id) as corrected_cases,
    ROUND(COUNT(f.feedback_id)::numeric / COUNT(*)::numeric * 100, 2) as correction_rate
FROM cases c
LEFT JOIN feedback f ON c.case_id = f.case_id;
```

### Get feedback for RLHF training
```sql
SELECT
    c.transcript,
    c.detected_language,
    c.ai_incident,
    c.ai_severity,
    c.ai_unit,
    f.corrected_incident,
    f.corrected_severity,
    f.corrected_unit
FROM feedback f
JOIN cases c ON f.case_id = c.case_id
ORDER BY f.timestamp DESC;
```

---

## Database Operations

### Initialize Database
```bash
python data/init_db.py
```

### Test Connection
```bash
python test_db_connection.py
```

### Backup Database
```bash
pg_dump -U postgres emergency_dispatch > backup.sql
```

### Restore Database
```bash
psql -U postgres emergency_dispatch < backup.sql
```

### Reset Database
```bash
# Drop and recreate
psql -U postgres -c "DROP DATABASE IF EXISTS emergency_dispatch;"
python data/init_db.py
```

---

## Connection Configuration

### Environment Variables (`.env`)
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=emergency_dispatch
DB_USER=postgres
DB_PASSWORD=postgres
```

### Config File (`config/config.yaml`)
```yaml
database:
  host: localhost
  port: 5432
  database: emergency_dispatch
  user: postgres
  password: postgres
  pool_size: 10
  max_overflow: 20
```

---

## Migrations

Migration scripts are located in `data/`:

| Script | Purpose |
|--------|---------|
| `init_db.py` | Initial schema creation |
| `migrate_add_unique_constraint.py` | Add UNIQUE constraint to feedback.case_id |
| `migrate_streaming_columns.py` | Add streaming-specific columns |

### Running Migrations
```bash
# Apply a specific migration
python data/migrate_add_unique_constraint.py
```

---

## Best Practices

1. **Always use parameterized queries** to prevent SQL injection
2. **Use transactions** for multi-step operations
3. **Close connections** after use (handled by connection pool)
4. **Use indexes** for frequently queried columns
5. **Cascade deletes** are enabled - deleting a case removes its feedback
