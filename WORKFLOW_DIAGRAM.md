# AI Emergency Dispatch Assistant - Workflow Diagram

## 🔄 Complete System Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EMERGENCY CALL RECEIVED                             │
│                               (Audio File)                                   │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 1: AUDIO UPLOAD                                 │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  POST /api/analyze-audio                                            │    │
│  │  • Upload: .wav, .mp3, .m4a, .flac, .ogg                           │    │
│  │  • Max Size: 50 MB                                                  │    │
│  │  • FastAPI receives and validates file                             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 2: SPEECH-TO-TEXT (STT)                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  🎤 STT Agent (OpenAI Whisper API)                                 │    │
│  │  ┌──────────────────────────────────────────────────────────┐     │    │
│  │  │  • Model: whisper-1                                       │     │    │
│  │  │  • Auto-detects language (Arabic/English)                │     │    │
│  │  │  • Converts audio → text transcript                      │     │    │
│  │  │  • Returns: text, language, duration, segments           │     │    │
│  │  └──────────────────────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  Output: "هناك حريق في المبنى" or "There's a fire in the building"        │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  STEP 3: LANGUAGE DETECTION                                  │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  🌐 Language Detection Agent (LangDetect)                          │    │
│  │  ┌──────────────────────────────────────────────────────────┐     │    │
│  │  │  • Confirms language: 'ar' (Arabic) or 'en' (English)    │     │    │
│  │  │  • Confidence threshold: 0.85                            │     │    │
│  │  │  • Selects appropriate rule sets                         │     │    │
│  │  └──────────────────────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  Output: language = "ar", confidence = 0.95                                 │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              STEP 4: PARALLEL AI CLASSIFICATION (3 Agents)                   │
│                                                                               │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐ │
│  │  🚨 Incident Agent   │  │  ⚡ Severity Agent   │  │  🚑 Dispatch     │ │
│  │                      │  │                      │  │     Agent        │ │
│  │  GPT-4 Turbo +       │  │  GPT-4 Turbo +       │  │  GPT-4 Turbo +   │ │
│  │  LangChain           │  │  LangChain           │  │  LangChain       │ │
│  │  ┌────────────────┐  │  │  ┌────────────────┐  │  │  ┌────────────┐ │ │
│  │  │ Rules (AR/EN)  │  │  │  │ Rules (AR/EN)  │  │  │  │ Rules      │ │ │
│  │  │ • MEDICAL      │  │  │  │ • CRITICAL     │  │  │  │ (AR/EN)    │ │ │
│  │  │ • POLICE       │  │  │  │ • HIGH         │  │  │  │ • AMBULANCE│ │ │
│  │  │ • FIRE         │  │  │  │ • MEDIUM       │  │  │  │ • POLICE   │ │ │
│  │  │ • OTHER        │  │  │  │ • LOW          │  │  │  │ • FIRE_DEPT│ │ │
│  │  └────────────────┘  │  │  └────────────────┘  │  │  │ • HAZMAT   │ │ │
│  │                      │  │                      │  │  │ • MULTIPLE │ │ │
│  │  Output:             │  │  Output:             │  │  └────────────┘ │ │
│  │  • Type: "FIRE"      │  │  • Level: "HIGH"     │  │                  │ │
│  │  • Confidence: 0.92  │  │  • Confidence: 0.88  │  │  Output:         │ │
│  │  • Keywords found    │  │  • Reasoning         │  │  • Unit: "FIRE_  │ │
│  │  • Reasoning         │  │                      │  │    DEPARTMENT"   │ │
│  │                      │  │                      │  │  • Confidence:   │ │
│  │                      │  │                      │  │    0.90          │ │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────┘ │
│                                                                               │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 5: SELF-EVALUATION                                   │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  ✅ Self-Evaluation Agent                                          │    │
│  │  ┌──────────────────────────────────────────────────────────┐     │    │
│  │  │  • Reviews all AI predictions                            │     │    │
│  │  │  • Checks consistency across classifications             │     │    │
│  │  │  • Validates against evaluation rules                    │     │    │
│  │  │  • Calculates overall confidence score                   │     │    │
│  │  │  • Flags cases for human review if needed                │     │    │
│  │  └──────────────────────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  Output: overall_confidence = 0.90, requires_review = false                 │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  STEP 6: SAVE TO DATABASE                                    │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  💾 PostgreSQL Database - "emergency_dispatch"                     │    │
│  │  ┌──────────────────────────────────────────────────────────┐     │    │
│  │  │  TABLE: cases                                             │     │    │
│  │  │  • id (UUID)                                              │     │    │
│  │  │  • audio_path                                             │     │    │
│  │  │  • transcript                                             │     │    │
│  │  │  • detected_language                                      │     │    │
│  │  │  • ai_incident (FIRE)                                     │     │    │
│  │  │  • ai_severity (HIGH)                                     │     │    │
│  │  │  • ai_dispatch_unit (FIRE_DEPARTMENT)                     │     │    │
│  │  │  • incident_confidence (0.92)                             │     │    │
│  │  │  • severity_confidence (0.88)                             │     │    │
│  │  │  • dispatch_confidence (0.90)                             │     │    │
│  │  │  • requires_review (false)                                │     │    │
│  │  │  • created_at (timestamp)                                 │     │    │
│  │  └──────────────────────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 7: API RESPONSE                                      │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  📤 Return JSON Response to Client                                 │    │
│  │  {                                                                  │    │
│  │    "case_id": "uuid-here",                                          │    │
│  │    "transcript": "هناك حريق في المبنى",                            │    │
│  │    "language": "ar",                                                │    │
│  │    "incident": {                                                    │    │
│  │      "type": "FIRE",                                                │    │
│  │      "confidence": 0.92                                             │    │
│  │    },                                                               │    │
│  │    "severity": {                                                    │    │
│  │      "level": "HIGH",                                               │    │
│  │      "confidence": 0.88                                             │    │
│  │    },                                                               │    │
│  │    "dispatch": {                                                    │    │
│  │      "unit": "FIRE_DEPARTMENT",                                     │    │
│  │      "confidence": 0.90                                             │    │
│  │    },                                                               │    │
│  │    "requires_review": false                                         │    │
│  │  }                                                                  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
    ┌───────────────────────────┐   ┌──────────────────────────┐
    │   OPERATOR REVIEWS        │   │   AUTO-DISPATCH          │
    │   (Human-in-the-Loop)     │   │   (High Confidence)      │
    └───────────┬───────────────┘   └──────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              STEP 8: OPERATOR FEEDBACK (Optional)                            │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  👤 Operator Reviews and Provides Corrections                      │    │
│  │  POST /api/operator-feedback                                        │    │
│  │  ┌──────────────────────────────────────────────────────────┐     │    │
│  │  │  • case_id: "uuid"                                        │     │    │
│  │  │  • corrected_incident: "FIRE" (confirmed or changed)      │     │    │
│  │  │  • corrected_severity: "CRITICAL" (upgraded)              │     │    │
│  │  │  • corrected_unit: "FIRE_DEPARTMENT_HAZMAT" (changed)     │     │    │
│  │  │  • operator_notes: "Chemical fire"                        │     │    │
│  │  └──────────────────────────────────────────────────────────┘     │    │
│  │                                                                     │    │
│  │  💾 Saves to DATABASE:                                             │    │
│  │  ┌──────────────────────────────────────────────────────────┐     │    │
│  │  │  TABLE: feedback                                          │     │    │
│  │  │  • id (UUID)                                              │     │    │
│  │  │  • case_id (Foreign Key)                                  │     │    │
│  │  │  • corrected_incident                                     │     │    │
│  │  │  • corrected_severity                                     │     │    │
│  │  │  • corrected_unit                                         │     │    │
│  │  │  • operator_notes                                         │     │    │
│  │  │  • created_at                                             │     │    │
│  │  └──────────────────────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              STEP 9: MODEL RETRAINING (RLHF - Optional)                      │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  🔄 Mini-RLHF Training                                             │    │
│  │  POST /api/retrain-model                                            │    │
│  │  ┌──────────────────────────────────────────────────────────┐     │    │
│  │  │  • Collects feedback from database                        │     │    │
│  │  │  • Minimum samples: 10                                    │     │    │
│  │  │  • Compares AI predictions vs operator corrections        │     │    │
│  │  │  • Updates model weights/prompts                          │     │    │
│  │  │  • Learning rate: 0.0001                                  │     │    │
│  │  │  • Batch size: 8, Epochs: 3                               │     │    │
│  │  │  • Improves future predictions                            │     │    │
│  │  └──────────────────────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│  Frequency: Daily or on-demand                                              │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                STEP 10: ANALYTICS & MONITORING                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  📊 Dashboard Analytics                                            │    │
│  │  GET /api/analytics                                                 │    │
│  │  ┌──────────────────────────────────────────────────────────┐     │    │
│  │  │  • Total cases processed                                  │     │    │
│  │  │  • AI acceptance rate (84.8%)                             │     │    │
│  │  │  • Edit rate (15.2%)                                      │     │    │
│  │  │  • Average confidence scores                              │     │    │
│  │  │  • Incident types distribution                            │     │    │
│  │  │  • Severity levels distribution                           │     │    │
│  │  │  • Language distribution                                  │     │    │
│  │  │  • Dispatch units distribution                            │     │    │
│  │  └──────────────────────────────────────────────────────────┘     │    │
│  │                                                                     │    │
│  │  🎨 Visual Dashboard (dashboard.html)                              │    │
│  │  • KPI Cards                                                        │    │
│  │  • Confidence Score Progress Bars                                  │    │
│  │  • Interactive Charts (Chart.js)                                    │    │
│  │  • Real-time Data Tables                                           │    │
│  │  • Auto-refresh every 30 seconds                                   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Summary

```
Audio File → STT → Language Detection → [Incident + Severity + Dispatch] →
Self-Eval → Database → Response → Operator Review → Feedback → RLHF →
Improved AI
```

---

## 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Web App    │  │  Mobile App  │  │   Dashboard  │              │
│  │   (Frontend) │  │   (Future)   │  │ (HTML/JS/CSS)│              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
└─────────┼──────────────────┼──────────────────┼─────────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                             │ HTTP/HTTPS
                             │
┌────────────────────────────▼─────────────────────────────────────────┐
│                         API LAYER (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  API Routers                                                 │    │
│  │  • /api/analyze-audio    • /api/operator-feedback           │    │
│  │  • /api/case/{id}        • /api/cases                       │    │
│  │  • /api/analytics        • /api/retrain-model               │    │
│  │  • /api/health           • /api/feedback/{id}               │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                             │                                         │
│  ┌─────────────────────────▼─────────────────────────────────┐      │
│  │         Main Controller                                    │      │
│  │  • Request validation                                      │      │
│  │  • Response formatting                                     │      │
│  │  • Error handling                                          │      │
│  └─────────────────────────────────────────────────────────────┘    │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────────┐
│                   CONTROLLER LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              Agent Controller                                │    │
│  │  • Orchestrates all AI agents                               │    │
│  │  • Manages workflow pipeline                                │    │
│  │  • Coordinates parallel processing                          │    │
│  └─────────────────────────────────────────────────────────────┘    │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────────┐
│                      AGENT LAYER (Multi-Agent System)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  STT Agent   │  │   Language   │  │   Incident   │               │
│  │  (Whisper)   │  │   Detection  │  │    Agent     │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Severity    │  │   Dispatch   │  │ Self-Eval    │               │
│  │    Agent     │  │    Agent     │  │    Agent     │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────────┐
│                       MODEL LAYER                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  AI Models                                                   │    │
│  │  • OpenAI Whisper API (STT)                                 │    │
│  │  • GPT-4 Turbo + LangChain (Classification)                 │    │
│  │  • LangDetect (Language)                                    │    │
│  │  • RLHF Trainer (Improvement)                               │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Rule Sets (JSON)                                           │    │
│  │  • config/emergency_rules/ar/                               │    │
│  │  • config/emergency_rules/en/                               │    │
│  └─────────────────────────────────────────────────────────────┘    │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────────┐
│                      DATA LAYER (PostgreSQL)                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Tables:                                                     │    │
│  │  ┌─────────────┐           ┌─────────────┐                 │    │
│  │  │   cases     │──────────▶│  feedback   │                 │    │
│  │  │             │  1-to-1   │             │                 │    │
│  │  │  • id (PK)  │           │  • id (PK)  │                 │    │
│  │  │  • audio    │           │  • case_id  │                 │    │
│  │  │  • transcript│          │    (FK)     │                 │    │
│  │  │  • ai_*     │           │  • corrected│                 │    │
│  │  │  • confidence│          │    _*       │                 │    │
│  │  │  • timestamps│          │  • notes    │                 │    │
│  │  └─────────────┘           └─────────────┘                 │    │
│  │                                                              │    │
│  │  Indexes: created_at, requires_review, case_id              │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🔀 Agent Interaction Flow

```
                         ┌────────────────┐
                         │  Audio Input   │
                         └────────┬───────┘
                                  │
                         ┌────────▼───────┐
                         │   STT Agent    │
                         │   (Sequential) │
                         └────────┬───────┘
                                  │
                         ┌────────▼───────┐
                         │  Language Agent│
                         │   (Sequential) │
                         └────────┬───────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
         ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
         │  Incident   │   │  Severity   │   │  Dispatch   │
         │   Agent     │   │   Agent     │   │   Agent     │
         │ (Parallel)  │   │ (Parallel)  │   │ (Parallel)  │
         └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
                │                 │                 │
                └─────────────────┼─────────────────┘
                                  │
                         ┌────────▼───────┐
                         │  Self-Eval     │
                         │   Agent        │
                         │  (Sequential)  │
                         └────────┬───────┘
                                  │
                         ┌────────▼───────┐
                         │   Database     │
                         │    Storage     │
                         └────────────────┘
```

---

## 📊 Feedback Loop Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTINUOUS IMPROVEMENT CYCLE                  │
│                                                                   │
│    ┌─────────────┐                           ┌─────────────┐    │
│    │ AI Analysis │─────────────┐            │  Improved   │    │
│    │  (Initial)  │             │            │   AI Model  │    │
│    └─────────────┘             │            └──────▲──────┘    │
│          │                     │                   │            │
│          │                     │                   │            │
│          ▼                     ▼                   │            │
│    ┌─────────────┐       ┌──────────┐      ┌──────┴──────┐    │
│    │  Database   │       │ Operator │      │    RLHF     │    │
│    │   Storage   │       │  Review  │      │  Training   │    │
│    └──────┬──────┘       └─────┬────┘      └──────▲──────┘    │
│           │                    │                   │            │
│           │                    │                   │            │
│           └────────────────────┼───────────────────┘            │
│                                │                                │
│                         ┌──────▼──────┐                         │
│                         │  Feedback   │                         │
│                         │   Storage   │                         │
│                         └─────────────┘                         │
│                                                                   │
│  Metrics Tracked:                                                │
│  • AI Acceptance Rate: 84.8%                                     │
│  • Edit Rate: 15.2%                                              │
│  • Operator Confirmed: Cases where AI was correct                │
│  • Edited Cases: Cases requiring corrections                     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Performance Indicators (KPIs)

```
┌───────────────────────────────────────────────────────────────┐
│                     SYSTEM METRICS                             │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  📊 Total Cases Processed: 250                                │
│                                                                │
│  ✅ AI Acceptance Rate: 84.8%                                 │
│      (Cases where AI was correct)                             │
│                                                                │
│  ✏️  Edit Rate: 15.2%                                         │
│      (Cases needing operator corrections)                     │
│                                                                │
│  👤 Review Rate: 18.0%                                        │
│      (Cases reviewed by operators)                            │
│                                                                │
│  🎯 Average Confidence Scores:                                │
│      • Incident:  87.5%                                       │
│      • Severity:  85.2%                                       │
│      • Dispatch:  89.1%                                       │
│                                                                │
│  🌐 Language Distribution:                                    │
│      • English (en): 72%                                      │
│      • Arabic (ar):  28%                                      │
│                                                                │
│  🚨 Top Incident Types:                                       │
│      • MEDICAL: 40%                                           │
│      • POLICE:  32%                                           │
│      • FIRE:    20%                                           │
│      • OTHER:    8%                                           │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔧 Deployment Workflow

```
┌────────────────────────────────────────────────────────────┐
│                   DEPLOYMENT OPTIONS                        │
└────────────────────────────────────────────────────────────┘

Option 1: Docker Compose (Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Set OPENAI_API_KEY
  2. docker-compose up -d
  3. System ready at http://localhost:8000

  Services:
  ┌──────────────────────────────────────┐
  │  Container: postgres                 │
  │  • PostgreSQL 15                     │
  │  • Port: 5432                        │
  │  • Auto-initialize database          │
  └──────────────────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────────┐
  │  Container: api                      │
  │  • FastAPI application               │
  │  • Port: 8000                        │
  │  • Health checks enabled             │
  └──────────────────────────────────────┘


Option 2: Local Development
━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Install PostgreSQL
  2. pip install -r requirements.txt
  3. Configure .env file
  4. python data/init_db.py
  5. python main.py

  ┌──────────────────┐
  │  PostgreSQL      │
  │  (localhost:5432)│
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │  FastAPI Server  │
  │  (localhost:8000)│
  └──────────────────┘
```

---

## 📁 File Structure & Workflow

```
.dev/
│
├── main.py                    # Application entry point
│   └─→ Initializes all components
│   └─→ Registers API routes
│   └─→ Starts FastAPI server
│
├── api/                       # API Layer
│   ├── audio_router.py        # POST /api/analyze-audio
│   ├── case_router.py         # GET/PUT/DELETE /api/case/{id}
│   ├── feedback_router.py     # POST /api/operator-feedback
│   ├── analytics_router.py    # GET /api/analytics
│   └── retrain_router.py      # POST /api/retrain-model
│
├── controllers/               # Business Logic Layer
│   ├── main_controller.py     # Orchestrates workflow
│   └── agent_controller.py    # Manages agents
│
├── agents/                    # Agent Layer
│   ├── stt_agent.py          # Speech-to-Text
│   ├── language_detection_agent.py
│   ├── incident_agent.py      # Classifies incident type
│   ├── severity_agent.py      # Assesses severity
│   ├── dispatch_agent.py      # Recommends units
│   └── self_eval_agent.py     # Quality check
│
├── models/                    # Model Layer
│   ├── stt_model.py          # Whisper API wrapper
│   ├── language_model.py      # LangDetect wrapper
│   ├── incident_classifier.py # GPT-4 + LangChain
│   ├── severity_classifier.py
│   ├── dispatch_classifier.py
│   └── rlhf_trainer.py        # Training logic
│
├── data/                      # Database Layer
│   └── init_db.py            # Database initialization
│
├── config/                    # Configuration
│   ├── config.yaml           # Main config
│   └── emergency_rules/      # Rule sets
│       ├── ar/               # Arabic rules
│       └── en/               # English rules
│
├── dashboard.html            # Analytics dashboard
│
└── tests/                    # Testing
    ├── unit/
    └── integration/
```

---

## 🚀 Quick Start Workflow

```
START
  │
  ├─→ Step 1: Clone Repository
  │
  ├─→ Step 2: Set Environment Variables
  │   └─→ OPENAI_API_KEY in .env
  │
  ├─→ Step 3: Choose Deployment Method
  │   ├─→ Docker: docker-compose up -d
  │   └─→ Local:  pip install → init DB → run server
  │
  ├─→ Step 4: Verify Health
  │   └─→ GET http://localhost:8000/api/health
  │
  ├─→ Step 5: Upload Audio
  │   └─→ POST http://localhost:8000/api/analyze-audio
  │
  ├─→ Step 6: View Results
  │   └─→ Response contains AI analysis
  │
  ├─→ Step 7: Submit Feedback (Optional)
  │   └─→ POST http://localhost:8000/api/operator-feedback
  │
  ├─→ Step 8: View Dashboard
  │   └─→ Open dashboard.html in browser
  │
  └─→ Step 9: Monitor & Improve
      └─→ POST http://localhost:8000/api/retrain-model
```

---

## 🎯 Summary

This workflow diagram illustrates:

1. **Complete Request Flow** - From audio upload to database storage
2. **Agent Architecture** - 6 specialized AI agents working in sequence/parallel
3. **System Layers** - API, Controller, Agent, Model, Data layers
4. **Feedback Loop** - Human-in-the-Loop with RLHF training
5. **Analytics** - Real-time monitoring and performance tracking
6. **Deployment** - Docker and local development options

The system is designed for **high availability**, **scalability**, and **continuous improvement** through operator feedback and machine learning.
