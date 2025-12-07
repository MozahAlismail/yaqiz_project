# Complete CRUD Operations Guide

## Overview

This document provides comprehensive examples for all CRUD (Create, Read, Update, Delete) operations available in the Emergency Dispatch API.

## One-to-One Relationship

**Important:** Each case can have only **ONE** feedback. This is enforced at the database level with a UNIQUE constraint on `feedback.case_id`.

```
┌──────────┐         ┌────────────┐
│  Case    │◄────────│  Feedback  │
│          │ 1     1 │            │
└──────────┘         └────────────┘
```

---

## Cases - CRUD Operations

### CREATE - Analyze Audio (Creates a Case)

```bash
curl -X POST http://localhost:8000/api/analyze-audio \
  -F "audio_file=@emergency_call.wav"
```

**Response:**
```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "transcript": "Fire in apartment building",
  "ai_incident": "FIRE",
  "status": "created"
}
```

---

### READ - Get Single Case

```bash
curl http://localhost:8000/api/case/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "transcript": "Fire in apartment building",
  "detected_language": "en",
  "language_confidence": 0.99,
  "ai_incident": "FIRE",
  "ai_severity": "CRITICAL",
  "ai_unit": "FIRE_DEPARTMENT",
  "incident_confidence": 0.95,
  "severity_confidence": 0.92,
  "dispatch_confidence": 0.98,
  "requires_review": false,
  "created_at": "2025-01-15T10:30:45"
}
```

---

### READ - Get All Cases (Paginated)

```bash
# First 50 cases
curl "http://localhost:8000/api/cases?limit=50&offset=0"

# Next 50 cases
curl "http://localhost:8000/api/cases?limit=50&offset=50"
```

**Response:**
```json
{
  "total": 250,
  "limit": 50,
  "offset": 0,
  "count": 50,
  "cases": [...]
}
```

---

### UPDATE - Modify Case Information

```bash
curl -X PUT http://localhost:8000/api/case/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "ai_incident": "FIRE",
    "ai_severity": "CRITICAL",
    "requires_review": false
  }'
```

**Updatable Fields:**
- `transcript`
- `detected_language`
- `language_confidence`
- `ai_incident`
- `ai_severity`
- `ai_unit`
- `incident_confidence`
- `severity_confidence`
- `dispatch_confidence`
- `requires_review`

**Response:**
```json
{
  "status": "success",
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "updated_fields": ["ai_incident", "ai_severity", "requires_review"]
}
```

---

### DELETE - Remove Case

⚠️ **WARNING:** This will also delete any associated feedback due to CASCADE constraint!

```bash
curl -X DELETE http://localhost:8000/api/case/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "status": "success",
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Case and associated feedback deleted"
}
```

---

## Feedback - CRUD Operations

### CREATE/UPDATE - Submit Feedback (UPSERT)

The `/api/operator-feedback` endpoint implements **UPSERT** logic:
- If feedback exists for the case → **UPDATE** it
- If no feedback exists → **CREATE** new one

**First submission (CREATE):**
```bash
curl -X POST http://localhost:8000/api/operator-feedback \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "550e8400-e29b-41d4-a716-446655440000",
    "corrected_incident": "FIRE",
    "corrected_severity": "CRITICAL",
    "corrected_unit": "FIRE_DEPARTMENT_HAZMAT",
    "operator_id": "operator_123"
  }'
```

**Response:**
```json
{
  "status": "success",
  "feedback_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "action": "created"
}
```

**Second submission for same case (UPDATE):**
```bash
curl -X POST http://localhost:8000/api/operator-feedback \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "550e8400-e29b-41d4-a716-446655440000",
    "corrected_incident": "MEDICAL",
    "corrected_severity": "HIGH",
    "corrected_unit": "AMBULANCE",
    "operator_id": "operator_456"
  }'
```

**Response:**
```json
{
  "status": "success",
  "feedback_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "action": "updated"
}
```

---

### READ - Get Single Feedback

```bash
curl http://localhost:8000/api/feedback/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response:**
```json
{
  "feedback_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "corrected_incident": "MEDICAL",
  "corrected_severity": "HIGH",
  "corrected_unit": "AMBULANCE",
  "operator_id": "operator_456",
  "timestamp": "2025-01-15T10:35:00"
}
```

---

### READ - Get All Feedbacks (Paginated)

```bash
curl "http://localhost:8000/api/feedbacks?limit=100&offset=0"
```

**Response includes case information:**
```json
{
  "total": 150,
  "limit": 100,
  "offset": 0,
  "count": 100,
  "feedbacks": [
    {
      "feedback_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "case_id": "550e8400-e29b-41d4-a716-446655440000",
      "corrected_incident": "MEDICAL",
      "corrected_severity": "HIGH",
      "corrected_unit": "AMBULANCE",
      "operator_id": "operator_456",
      "timestamp": "2025-01-15T10:35:00",
      "transcript": "Fire in apartment building",
      "ai_incident": "FIRE",
      "ai_severity": "CRITICAL",
      "ai_unit": "FIRE_DEPARTMENT"
    }
  ]
}
```

---

### UPDATE - Modify Feedback by ID

```bash
curl -X PUT http://localhost:8000/api/feedback/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Content-Type: application/json" \
  -d '{
    "corrected_incident": "FIRE",
    "corrected_severity": "CRITICAL"
  }'
```

**Updatable Fields:**
- `corrected_incident`
- `corrected_severity`
- `corrected_unit`
- `operator_id`

**Note:** `timestamp` is automatically updated.

**Response:**
```json
{
  "status": "success",
  "feedback_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "updated_fields": ["corrected_incident", "corrected_severity"]
}
```

---

### DELETE - Remove Feedback

```bash
curl -X DELETE http://localhost:8000/api/feedback/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response:**
```json
{
  "status": "success",
  "feedback_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "Feedback deleted"
}
```

**Note:** The associated case remains intact.

---

## Python Examples

### Complete CRUD Workflow

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. CREATE - Upload audio (creates case)
with open("emergency_call.wav", "rb") as audio_file:
    files = {"audio_file": audio_file}
    response = requests.post(f"{BASE_URL}/analyze-audio", files=files)
    case = response.json()
    case_id = case["case_id"]
    print(f"Case created: {case_id}")

# 2. READ - Get the case
response = requests.get(f"{BASE_URL}/case/{case_id}")
case_data = response.json()
print(f"Case transcript: {case_data['transcript']}")

# 3. CREATE FEEDBACK - First submission
feedback_data = {
    "case_id": case_id,
    "corrected_incident": "FIRE",
    "corrected_severity": "CRITICAL",
    "corrected_unit": "FIRE_DEPARTMENT",
    "operator_id": "operator_001"
}
response = requests.post(f"{BASE_URL}/operator-feedback", json=feedback_data)
feedback_result = response.json()
print(f"Feedback {feedback_result['action']}: {feedback_result['feedback_id']}")

# 4. UPDATE FEEDBACK - Submit again (same case_id)
feedback_data["corrected_severity"] = "HIGH"
response = requests.post(f"{BASE_URL}/operator-feedback", json=feedback_data)
feedback_result = response.json()
print(f"Feedback {feedback_result['action']}: {feedback_result['feedback_id']}")

# 5. UPDATE CASE - Modify case fields
update_data = {"requires_review": True}
response = requests.put(f"{BASE_URL}/case/{case_id}", json=update_data)
print(f"Case updated: {response.json()}")

# 6. READ ALL - Get all cases and feedbacks
response = requests.get(f"{BASE_URL}/cases", params={"limit": 10})
cases = response.json()
print(f"Total cases: {cases['total']}")

response = requests.get(f"{BASE_URL}/feedbacks", params={"limit": 10})
feedbacks = response.json()
print(f"Total feedbacks: {feedbacks['total']}")

# 7. DELETE FEEDBACK - Remove feedback only
feedback_id = feedback_result["feedback_id"]
response = requests.delete(f"{BASE_URL}/feedback/{feedback_id}")
print(f"Feedback deleted: {response.json()}")

# 8. DELETE CASE - Remove case (and any remaining feedback)
response = requests.delete(f"{BASE_URL}/case/{case_id}")
print(f"Case deleted: {response.json()}")
```

---

## Database Schema

### One-to-One Relationship Enforcement

```sql
CREATE TABLE cases (
    case_id VARCHAR(36) PRIMARY KEY,
    transcript TEXT NOT NULL,
    -- ... other fields
);

CREATE TABLE feedback (
    feedback_id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL UNIQUE,  -- ← UNIQUE constraint
    corrected_incident VARCHAR(100),
    corrected_severity VARCHAR(50),
    corrected_unit VARCHAR(100),
    operator_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
);
```

**Key Points:**
1. `UNIQUE` constraint on `case_id` ensures one feedback per case
2. `ON DELETE CASCADE` means deleting a case also deletes its feedback
3. Deleting feedback does NOT delete the case

---

## Migration Script

If you have an existing database, run the migration:

```bash
python data/migrate_add_unique_constraint.py
```

This will:
1. Check for duplicate feedbacks
2. Keep only the most recent feedback for each case
3. Add the UNIQUE constraint

---

## Best Practices

### 1. Always Use UPSERT for Feedback

```python
# ✅ GOOD - Use POST which handles create/update
requests.post(f"{BASE_URL}/operator-feedback", json=feedback_data)

# ❌ BAD - Don't check and then decide
# This creates race conditions
```

### 2. Handle Both Actions in Response

```python
response = requests.post(f"{BASE_URL}/operator-feedback", json=feedback_data)
result = response.json()

if result["action"] == "created":
    print("New feedback created")
elif result["action"] == "updated":
    print("Existing feedback updated")
```

### 3. Be Careful with DELETE Case

```python
# Deleting a case also deletes its feedback
response = requests.delete(f"{BASE_URL}/case/{case_id}")

# To delete only feedback:
response = requests.delete(f"{BASE_URL}/feedback/{feedback_id}")
```

---

## Error Handling

### 404 - Not Found
```json
{
  "detail": "Case not found"
}
```

### 400 - Bad Request
```json
{
  "detail": "No valid fields to update"
}
```

### 500 - Server Error
```json
{
  "detail": "Database connection failed"
}
```

---

## Testing

### Test the One-to-One Constraint

```bash
# 1. Create a case
curl -X POST http://localhost:8000/api/analyze-audio \
  -F "audio_file=@test.wav"

# 2. Submit first feedback (creates)
curl -X POST http://localhost:8000/api/operator-feedback \
  -H "Content-Type: application/json" \
  -d '{"case_id": "YOUR_CASE_ID", "corrected_incident": "FIRE"}'

# Result: {"action": "created"}

# 3. Submit second feedback (updates same feedback)
curl -X POST http://localhost:8000/api/operator-feedback \
  -H "Content-Type: application/json" \
  -d '{"case_id": "YOUR_CASE_ID", "corrected_incident": "MEDICAL"}'

# Result: {"action": "updated"}  ← Same feedback_id, updated values
```

---

## Summary

| Operation | Cases | Feedback |
|-----------|-------|----------|
| **Create** | POST /analyze-audio | POST /operator-feedback |
| **Read One** | GET /case/{id} | GET /feedback/{id} |
| **Read All** | GET /cases | GET /feedbacks |
| **Update** | PUT /case/{id} | PUT /feedback/{id} OR POST /operator-feedback |
| **Delete** | DELETE /case/{id} | DELETE /feedback/{id} |

**Remember:**
- ✅ One case = One feedback (enforced)
- ✅ POST /operator-feedback does UPSERT
- ⚠️ DELETE case → deletes feedback too
- ✅ DELETE feedback → case remains
