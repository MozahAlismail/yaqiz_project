# realtime Audio Analysis Workflow Documentation

## Overview
This document explains the single-pass classification workflow for the `/api/realtime-audio-analyze` endpoint.

---

## 🔄 Complete Workflow

### **Scenario 1: Translation ENABLED (translate=True)**

```
Input: English audio file, translate=true, target_language="ar"

Step 1: Transcription
├─ Audio → faster-whisper → Transcript
├─ Result: "There's a fire in my house!"
└─ Detected Language: "en"

Step 2: Translation
├─ Original: "There's a fire in my house!" (en)
├─ TranslationModel (GPT-4o-mini)
└─ Translated: "هناك حريق في منزلي!" (ar)

Step 3: Language Selection for Classification
├─ text_for_classification = "هناك حريق في منزلي!" (TRANSLATED)
├─ language_for_classification = "ar" (TARGET LANGUAGE)
└─ Rules Path: config/emergency_rules/ar/*_rules.json

Step 4: Classification (HAPPENS ONCE)
├─ IncidentClassifier.classify(
│   text="هناك حريق في منزلي!",
│   language="ar"
│ )
│ ├─ Loads: config/emergency_rules/ar/incident_rules.json
│ ├─ Prompt includes: language="ar"
│ └─ Response: {
│       "incident_type": "FIRE",
│       "confidence": 0.95,
│       "reasoning": "تم اكتشاف كلمات حريق ومنزل",  ← IN ARABIC
│       "keywords_found": ["حريق", "منزل"]  ← IN ARABIC
│     }
│
├─ SeverityClassifier.classify(
│   text="هناك حريق في منزلي!",
│   incident_type="FIRE",
│   language="ar"
│ )
│ ├─ Loads: config/emergency_rules/ar/severity_rules.json
│ ├─ Prompt includes: language="ar"
│ └─ Response: {
│       "severity_level": "HIGH",
│       "confidence": 0.92,
│       "reasoning": "حريق نشط في مبنى سكني",  ← IN ARABIC
│       "urgency_indicators": ["حريق", "منزل"]  ← IN ARABIC
│     }
│
└─ DispatchClassifier.classify(
    text="هناك حريق في منزلي!",
    incident_type="FIRE",
    severity_level="HIGH",
    language="ar"
  )
  ├─ Loads: config/emergency_rules/ar/dispatch_rules.json
  ├─ Prompt includes: language="ar"
  └─ Response: {
        "dispatch_unit": "FIRE",
        "confidence": 0.98,
        "reasoning": "حريق خطير يتطلب فرقة الإطفاء",  ← IN ARABIC
        "estimated_priority": "أولوية 1"  ← IN ARABIC
      }

Final Response:
{
  "original_transcript": "There's a fire in my house!",
  "detected_language": "en",
  "translated_text": "هناك حريق في منزلي!",
  "translated_language": "ar",
  "classification": {
    "incident": { ... },  ← ALL IN ARABIC
    "severity": { ... },  ← ALL IN ARABIC
    "dispatch": { ... }   ← ALL IN ARABIC
  }
}
```

---

### **Scenario 2: Translation DISABLED (translate=False)**

```
Input: Arabic audio file, translate=false

Step 1: Transcription
├─ Audio → faster-whisper → Transcript
├─ Result: "هناك حريق في منزلي!"
└─ Detected Language: "ar"

Step 2: Translation
└─ SKIPPED (translate=false)

Step 3: Language Selection for Classification
├─ text_for_classification = "هناك حريق في منزلي!" (ORIGINAL)
├─ language_for_classification = "ar" (DETECTED LANGUAGE)
└─ Rules Path: config/emergency_rules/ar/*_rules.json

Step 4: Classification (HAPPENS ONCE)
├─ IncidentClassifier.classify(
│   text="هناك حريق في منزلي!",
│   language="ar"
│ )
│ ├─ Loads: config/emergency_rules/ar/incident_rules.json
│ ├─ Prompt includes: language="ar"
│ └─ Response: {
│       "incident_type": "FIRE",
│       "confidence": 0.95,
│       "reasoning": "تم اكتشاف كلمات حريق ومنزل",  ← IN ARABIC
│       "keywords_found": ["حريق", "منزل"]  ← IN ARABIC
│     }
│
└─ [Similar for Severity and Dispatch - ALL IN ARABIC]

Final Response:
{
  "original_transcript": "هناك حريق في منزلي!",
  "detected_language": "ar",
  "translated_text": null,
  "translated_language": null,
  "classification": {
    "incident": { ... },  ← ALL IN ARABIC
    "severity": { ... },  ← ALL IN ARABIC
    "dispatch": { ... }   ← ALL IN ARABIC
  }
}
```

---

## ✅ Key Guarantees

### 1. **Single Classification**
- Classification happens **EXACTLY ONCE**
- No duplicate processing
- No re-classification for different languages

### 2. **Correct Language Rules**
```python
if translate and translated_text:
    language_for_classification = target_language  # e.g., "ar"
    rules_path = f"config/emergency_rules/{target_language}/"
else:
    language_for_classification = detected_language  # e.g., "en"
    rules_path = f"config/emergency_rules/{detected_language}/"
```

### 3. **Language-Consistent Responses**
- If `language_for_classification = "ar"`:
  - Rules loaded from `config/emergency_rules/ar/`
  - Prompts explicitly request responses in Arabic
  - ALL results (reasoning, keywords, indicators) in Arabic

- If `language_for_classification = "en"`:
  - Rules loaded from `config/emergency_rules/en/`
  - Prompts explicitly request responses in English
  - ALL results (reasoning, keywords, indicators) in English

---

## 🔍 Classification Logic Decision Tree

```
┌─────────────────────────────────────────┐
│ Audio File Received                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ Transcribe with faster-whisper          │
│ Result: full_transcript, detected_lang  │
└──────────────┬───────────────────────────┘
               │
               ▼
          ┌────────┐
          │translate?│
          └───┬────┬─┘
              │    │
         Yes  │    │  No
              │    │
              ▼    ▼
    ┌─────────────┐  ┌──────────────────┐
    │ Translate   │  │ Use Original     │
    │ to target   │  │ Transcript       │
    │ language    │  │                  │
    └──────┬──────┘  └────────┬─────────┘
           │                  │
           │                  │
           ▼                  ▼
    ┌──────────────────────────────────┐
    │ Select Text & Language           │
    │                                  │
    │ IF translate=True:               │
    │   text = translated_text         │
    │   lang = target_language         │
    │                                  │
    │ IF translate=False:              │
    │   text = original_transcript     │
    │   lang = detected_language       │
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ CLASSIFY ONCE                    │
    │                                  │
    │ Load rules from:                 │
    │   config/emergency_rules/{lang}/ │
    │                                  │
    │ Classifiers return results in:   │
    │   {lang} language                │
    └──────────────┬───────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ Return Complete Results          │
    │ - Original transcript            │
    │ - Translation (if enabled)       │
    │ - Classification in {lang}       │
    └──────────────────────────────────┘
```

---

## 📊 Examples

### Example 1: English → Arabic with Translation
```json
Request:
  audio: "emergency.wav" (English speaker)
  translate: true
  target_language: "ar"

Process:
  1. Transcribe: "There's a fire at 123 Main Street!"
  2. Detect: language = "en"
  3. Translate: "هناك حريق في شارع ماين 123!"
  4. Classify using Arabic text + Arabic rules

Response:
{
  "original_transcript": "There's a fire at 123 Main Street!",
  "detected_language": "en",
  "translated_text": "هناك حريق في شارع ماين 123!",
  "translated_language": "ar",
  "classification": {
    "incident": {
      "incident_type": "FIRE",
      "reasoning": "تم اكتشاف حريق في موقع محدد"  ← Arabic
    }
  }
}
```

### Example 2: Arabic Audio without Translation
```json
Request:
  audio: "emergency_ar.wav" (Arabic speaker)
  translate: false

Process:
  1. Transcribe: "هناك حريق في شارع ماين 123!"
  2. Detect: language = "ar"
  3. Skip translation
  4. Classify using Arabic text + Arabic rules

Response:
{
  "original_transcript": "هناك حريق في شارع ماين 123!",
  "detected_language": "ar",
  "translated_text": null,
  "translated_language": null,
  "classification": {
    "incident": {
      "incident_type": "FIRE",
      "reasoning": "تم اكتشاف حريق في موقع محدد"  ← Arabic
    }
  }
}
```

---

## 🎯 Summary

| Aspect | Implementation |
|--------|----------------|
| **Classification Count** | EXACTLY ONCE per request |
| **Rules Selection** | Based on `target_language` (if translate) or `detected_language` (if no translate) |
| **Response Language** | ALL responses in classification language |
| **Text Used** | `translated_text` (if translate) or `original_transcript` (if no translate) |
| **No Duplication** | Single pass through classification pipeline |
| **Language Consistency** | Rules, prompts, and responses all in same language |

---

## 🔧 Configuration Files Used

Based on classification language:
- `config/emergency_rules/{language}/incident_rules.json`
- `config/emergency_rules/{language}/severity_rules.json`
- `config/emergency_rules/{language}/dispatch_rules.json`
- `config/prompts/incident_prompt.txt` (with language parameter)
- `config/prompts/severity_prompt.txt` (with language parameter)
- `config/prompts/dispatch_prompt.txt` (with language parameter)
