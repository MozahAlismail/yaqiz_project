# API Examples

Complete guide to using the Emergency Dispatch API endpoints.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required (add in production).

---

## Cases Endpoints

### 1. Get Single Case

Retrieve a specific case by its ID.

**Endpoint:** `GET /api/case/{case_id}`

**Example:**
```bash
curl http://localhost:8000/api/case/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

**Response:**
```json
{
  "case_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "transcript": "There is a fire in my apartment building",
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

### 2. Get All Cases (Paginated)

Retrieve all cases with pagination support.

**Endpoint:** `GET /api/cases`

**Query Parameters:**
- `limit` (optional): Maximum number of cases to return (1-1000, default: 100)
- `offset` (optional): Number of cases to skip (default: 0)

**Example 1 - First 50 cases:**
```bash
curl http://localhost:8000/api/cases?limit=50&offset=0
```

**Example 2 - Next 50 cases (pagination):**
```bash
curl http://localhost:8000/api/cases?limit=50&offset=50
```

**Example 3 - Default (100 cases):**
```bash
curl http://localhost:8000/api/cases
```

**Response:**
```json
{
  "total": 250,
  "limit": 50,
  "offset": 0,
  "count": 50,
  "cases": [
    {
      "case_id": "uuid-1",
      "transcript": "Medical emergency...",
      "detected_language": "en",
      "ai_incident": "MEDICAL",
      "ai_severity": "HIGH",
      "created_at": "2025-01-15T12:00:00"
    },
    {
      "case_id": "uuid-2",
      "transcript": "حريق في المبنى...",
      "detected_language": "ar",
      "ai_incident": "FIRE",
      "ai_severity": "CRITICAL",
      "created_at": "2025-01-15T11:45:00"
    }
    // ... more cases
  ]
}
```

**Pagination Logic:**
```python
# Page 1 (first 100 items)
GET /api/cases?limit=100&offset=0

# Page 2 (next 100 items)
GET /api/cases?limit=100&offset=100

# Page 3 (next 100 items)
GET /api/cases?limit=100&offset=200
```

---

## Feedback Endpoints

### 3. Get Single Feedback

Retrieve a specific feedback by its ID.

**Endpoint:** `GET /api/feedback/{feedback_id}`

**Example:**
```bash
curl http://localhost:8000/api/feedback/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response:**
```json
{
  "feedback_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "case_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "corrected_incident": "FIRE",
  "corrected_severity": "CRITICAL",
  "corrected_unit": "FIRE_DEPARTMENT_HAZMAT",
  "operator_id": "operator_123",
  "timestamp": "2025-01-15T10:35:00"
}
```

---

### 4. Get All Feedbacks (Paginated)

Retrieve all feedbacks with case information.

**Endpoint:** `GET /api/feedbacks`

**Query Parameters:**
- `limit` (optional): Maximum number of feedbacks to return (1-1000, default: 100)
- `offset` (optional): Number of feedbacks to skip (default: 0)

**Example:**
```bash
curl http://localhost:8000/api/feedbacks?limit=25&offset=0
```

**Response:**
```json
{
  "total": 150,
  "limit": 25,
  "offset": 0,
  "count": 25,
  "feedbacks": [
    {
      "feedback_id": "uuid-fb-1",
      "case_id": "uuid-case-1",
      "corrected_incident": "MEDICAL",
      "corrected_severity": "HIGH",
      "corrected_unit": "AMBULANCE",
      "operator_id": "operator_456",
      "timestamp": "2025-01-15T12:10:00",
      "transcript": "Person having chest pain...",
      "ai_incident": "MEDICAL",
      "ai_severity": "MEDIUM",
      "ai_unit": "AMBULANCE"
    }
    // ... more feedbacks
  ]
}
```

**Note:** Feedbacks include both the corrections and original AI predictions from the case.

---

### 5. Submit Feedback

Submit operator corrections for a case.

**Endpoint:** `POST /api/operator-feedback`

**Request Body:**
```json
{
  "case_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "corrected_incident": "FIRE",
  "corrected_severity": "CRITICAL",
  "corrected_unit": "FIRE_DEPARTMENT_HAZMAT",
  "operator_id": "operator_123"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/operator-feedback \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
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
  "feedback_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## Audio Analysis

### 6. Analyze Audio

Transcribe and analyze an emergency audio file.

**Endpoint:** `POST /api/analyze-audio`

**Example:**
```bash
curl -X POST http://localhost:8000/api/analyze-audio \
  -F "audio_file=@emergency_call.wav"
```

**Response:**
```json
{
  "case_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "transcript": "There is a fire in my apartment building on the third floor",
  "detected_language": "en",
  "language_confidence": 0.99,
  "incident_type": "FIRE",
  "severity_level": "CRITICAL",
  "dispatch_unit": "FIRE_DEPARTMENT",
  "incident_confidence": 0.95,
  "severity_confidence": 0.92,
  "dispatch_confidence": 0.98,
  "requires_human_review": false,
  "self_evaluation": {
    "overall_quality": "HIGH",
    "reasoning": "Clear emergency with high confidence predictions"
  }
}
```

**Supported Audio Formats:**
- WAV, MP3, M4A
- MP4, MPEG, MPGA
- WEBM
- Max file size: 25MB

---

## Python Examples

### Using `requests` library

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Get all cases (first page)
response = requests.get(f"{BASE_URL}/cases", params={"limit": 50, "offset": 0})
data = response.json()
print(f"Total cases: {data['total']}")
print(f"Retrieved: {data['count']} cases")

# Get specific case
case_id = data['cases'][0]['case_id']
response = requests.get(f"{BASE_URL}/case/{case_id}")
case = response.json()
print(f"Case: {case['transcript']}")

# Get all feedbacks
response = requests.get(f"{BASE_URL}/feedbacks", params={"limit": 100})
feedbacks = response.json()
print(f"Total feedbacks: {feedbacks['total']}")

# Submit feedback
feedback_data = {
    "case_id": case_id,
    "corrected_incident": "FIRE",
    "corrected_severity": "CRITICAL",
    "corrected_unit": "FIRE_DEPARTMENT",
    "operator_id": "operator_001"
}
response = requests.post(f"{BASE_URL}/operator-feedback", json=feedback_data)
print(f"Feedback submitted: {response.json()}")
```

---

## JavaScript/Fetch Examples

```javascript
const BASE_URL = "http://localhost:8000/api";

// Get all cases
async function getAllCases(limit = 100, offset = 0) {
  const response = await fetch(`${BASE_URL}/cases?limit=${limit}&offset=${offset}`);
  const data = await response.json();
  console.log(`Total cases: ${data.total}`);
  return data.cases;
}

// Get specific case
async function getCase(caseId) {
  const response = await fetch(`${BASE_URL}/case/${caseId}`);
  return await response.json();
}

// Get all feedbacks
async function getAllFeedbacks(limit = 100, offset = 0) {
  const response = await fetch(`${BASE_URL}/feedbacks?limit=${limit}&offset=${offset}`);
  const data = await response.json();
  return data.feedbacks;
}

// Submit feedback
async function submitFeedback(feedbackData) {
  const response = await fetch(`${BASE_URL}/operator-feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(feedbackData)
  });
  return await response.json();
}

// Usage
getAllCases(50, 0).then(cases => {
  console.log("Cases:", cases);
});
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Case not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Database connection failed"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 1000",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Swagger UI Documentation

Interactive API documentation available at:

```
http://localhost:8000/docs
```

Features:
- Try out endpoints directly
- See request/response schemas
- Download OpenAPI specification

---

## Pagination Best Practices

1. **Start with default limit:**
   ```bash
   GET /api/cases  # Returns first 100 cases
   ```

2. **Calculate total pages:**
   ```python
   import math

   response = requests.get(f"{BASE_URL}/cases")
   data = response.json()

   total_items = data['total']
   items_per_page = data['limit']
   total_pages = math.ceil(total_items / items_per_page)
   ```

3. **Iterate through pages:**
   ```python
   def get_all_items(endpoint, limit=100):
       offset = 0
       all_items = []

       while True:
           response = requests.get(
               f"{BASE_URL}/{endpoint}",
               params={"limit": limit, "offset": offset}
           )
           data = response.json()

           all_items.extend(data.get('cases') or data.get('feedbacks'))

           if offset + limit >= data['total']:
               break

           offset += limit

       return all_items
   ```

---

## Rate Limiting

Currently no rate limiting (recommended for production):
- Implement rate limiting middleware
- Suggested: 100 requests per minute per IP
- Return 429 status code when exceeded

---

## Next Steps

1. Test endpoints using Swagger UI: http://localhost:8000/docs
2. Implement authentication for production
3. Add filtering and sorting parameters
4. Set up monitoring for endpoint usage
