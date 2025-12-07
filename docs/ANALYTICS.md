# Dashboard Analytics Guide

## Overview

The analytics endpoint provides comprehensive statistics and metrics for building dashboards and monitoring system performance.

## Endpoint

**GET** `/api/analytics`

Returns comprehensive analytics including:
- Feedback analysis (edited vs correct cases)
- Average AI confidence scores
- Incident types distribution
- Language distribution
- Severity levels distribution

All metrics include both **counts** and **percentages** for easy visualization.

---

## Example Request

```bash
curl http://localhost:8000/api/analytics
```

---

## Example Response

```json
{
  "total_cases": 250,
  "feedback_analysis": {
    "total_cases": 250,
    "edited_cases": 38,
    "correct_cases": 212,
    "operator_confirmed": 7,
    "unreviewed_cases": 205,
    "edit_rate": 0.152,
    "acceptance_rate": 0.848,
    "review_rate": 0.18
  },
  "confidence_scores": {
    "incident": {
      "average": 0.8745,
      "total_cases": 250
    },
    "severity": {
      "average": 0.8523,
      "total_cases": 250
    },
    "dispatch": {
      "average": 0.8912,
      "total_cases": 250
    }
  },
  "incident_types": {
    "MEDICAL": {
      "count": 100,
      "percentage": 40.0
    },
    "POLICE": {
      "count": 80,
      "percentage": 32.0
    },
    "FIRE": {
      "count": 50,
      "percentage": 20.0
    },
    "OTHER": {
      "count": 20,
      "percentage": 8.0
    }
  },
  "languages": {
    "en": {
      "count": 180,
      "percentage": 72.0
    },
    "ar": {
      "count": 70,
      "percentage": 28.0
    }
  },
  "severity_levels": {
    "CRITICAL": {
      "count": 30,
      "percentage": 12.0
    },
    "HIGH": {
      "count": 80,
      "percentage": 32.0
    },
    "MEDIUM": {
      "count": 100,
      "percentage": 40.0
    },
    "LOW": {
      "count": 40,
      "percentage": 16.0
    }
  },
  "dispatch_units": {
    "AMBULANCE": {
      "count": 100,
      "percentage": 40.0
    },
    "POLICE": {
      "count": 80,
      "percentage": 32.0
    },
    "FIRE_DEPARTMENT": {
      "count": 50,
      "percentage": 20.0
    },
    "FIRE_DEPARTMENT_HAZMAT": {
      "count": 20,
      "percentage": 8.0
    }
  }
}
```

---

## Response Fields

### 1. Total Cases
```json
"total_cases": 250
```
Total number of emergency cases in the database.

---

### 2. Feedback Analysis

Shows how many cases were actually edited by operators vs accepted as correct.

```json
"feedback_analysis": {
  "total_cases": 250,
  "edited_cases": 38,         // Cases where operator CHANGED AI predictions
  "correct_cases": 212,       // Cases where AI was correct (confirmed + unreviewed)
  "operator_confirmed": 7,    // Cases where operator REVIEWED and AGREED with AI
  "unreviewed_cases": 205,    // Cases with no feedback yet
  "edit_rate": 0.152,         // 15.2% of cases needed correction
  "acceptance_rate": 0.848,   // 84.8% of cases were correct
  "review_rate": 0.18         // 18% of cases were reviewed (edited + confirmed)
}
```

**Key Metrics:**
- `edited_cases`: Cases where feedback exists AND values differ from AI predictions
  - Checks if `corrected_incident ≠ ai_incident` OR `corrected_severity ≠ ai_severity` OR `corrected_unit ≠ ai_unit`
- `operator_confirmed`: Cases where feedback exists AND all values match AI predictions
  - Operator reviewed the case and agreed with AI
- `unreviewed_cases`: Cases with no feedback submitted yet
- `correct_cases`: Total correct cases = `operator_confirmed + unreviewed_cases`
- `edit_rate`: Percentage that needed correction = `edited_cases / total_cases`
- `acceptance_rate`: Percentage that were correct = `correct_cases / total_cases`
- `review_rate`: Percentage reviewed by operators = `(edited_cases + operator_confirmed) / total_cases`

**Important:** This uses intelligent comparison logic - it checks if feedback actually differs from AI predictions, not just if feedback exists.

**Use Cases:**
- Monitor true AI accuracy (not just reviewed vs unreviewed)
- Track operator workload and review patterns
- Identify when model needs retraining (high edit_rate)
- Recognize operator trust in AI (high operator_confirmed)

---

### 3. Confidence Scores

Average AI confidence scores across all predictions.

```json
"confidence_scores": {
  "incident": {
    "average": 0.8745,      // 87.45% average confidence
    "total_cases": 250
  },
  "severity": {
    "average": 0.8523,      // 85.23% average confidence
    "total_cases": 250
  },
  "dispatch": {
    "average": 0.8912,      // 89.12% average confidence
    "total_cases": 250
  }
}
```

**Interpretation:**
- Values range from 0.0 to 1.0 (0% to 100%)
- Higher values indicate more confident predictions
- Low confidence may indicate need for human review

**Use Cases:**
- Set thresholds for automatic dispatch (e.g., confidence > 0.90)
- Identify cases requiring human review (e.g., confidence < 0.70)
- Monitor model performance trends

---

### 4. Incident Types Distribution

Breakdown of emergency types handled by the system.

```json
"incident_types": {
  "MEDICAL": {
    "count": 100,
    "percentage": 40.0
  },
  "POLICE": {
    "count": 80,
    "percentage": 32.0
  },
  "FIRE": {
    "count": 50,
    "percentage": 20.0
  },
  "OTHER": {
    "count": 20,
    "percentage": 8.0
  }
}
```

**Common Incident Types:**
- `MEDICAL`: Medical emergencies, injuries, health issues
- `POLICE`: Crimes, disturbances, law enforcement needs
- `FIRE`: Fires, explosions, hazmat situations
- `OTHER`: Uncategorized or mixed emergencies

**Use Cases:**
- Resource allocation planning
- Staff training prioritization
- Identify trending emergency types

---

### 5. Languages Distribution

Distribution of detected languages in emergency calls.

```json
"languages": {
  "en": {
    "count": 180,
    "percentage": 72.0
  },
  "ar": {
    "count": 70,
    "percentage": 28.0
  }
}
```

**Language Codes:**
- `en`: English
- `ar`: Arabic
- May include other languages detected by Whisper

**Use Cases:**
- Staffing decisions (multilingual operators)
- Translation service needs
- Community outreach planning

---

### 6. Severity Levels Distribution

Distribution of emergency severity classifications.

```json
"severity_levels": {
  "CRITICAL": {
    "count": 30,
    "percentage": 12.0
  },
  "HIGH": {
    "count": 80,
    "percentage": 32.0
  },
  "MEDIUM": {
    "count": 100,
    "percentage": 40.0
  },
  "LOW": {
    "count": 40,
    "percentage": 16.0
  }
}
```

**Severity Levels (Ordered by Priority):**
1. `CRITICAL`: Life-threatening, immediate response required
2. `HIGH`: Urgent, priority response needed
3. `MEDIUM`: Important, standard response time
4. `LOW`: Non-urgent, routine handling

**Use Cases:**
- Emergency response prioritization
- Resource deployment strategies
- Performance metrics (response times by severity)

---

### 7. Dispatch Units Distribution

Distribution of recommended emergency response units.

```json
"dispatch_units": {
  "AMBULANCE": {
    "count": 100,
    "percentage": 40.0
  },
  "POLICE": {
    "count": 80,
    "percentage": 32.0
  },
  "FIRE_DEPARTMENT": {
    "count": 50,
    "percentage": 20.0
  },
  "FIRE_DEPARTMENT_HAZMAT": {
    "count": 20,
    "percentage": 8.0
  }
}
```

**Common Dispatch Units:**
- `AMBULANCE`: Medical emergencies, injuries, health-related calls
- `POLICE`: Law enforcement needs, crimes, disturbances
- `FIRE_DEPARTMENT`: Fire incidents, basic rescue operations
- `FIRE_DEPARTMENT_HAZMAT`: Hazardous materials, chemical incidents
- `FIRE_DEPARTMENT_RESCUE`: Technical rescue, water rescue
- `MULTIPLE_UNITS`: Complex emergencies requiring multiple services

**Use Cases:**
- Resource allocation and availability planning
- Unit deployment optimization
- Cross-training requirements (incidents needing multiple units)
- Response capacity analysis

---

## Python Example

```python
import requests

# Get analytics
response = requests.get("http://localhost:8000/api/analytics")
analytics = response.json()

# Display key metrics
fb = analytics['feedback_analysis']
print(f"Total Cases: {analytics['total_cases']}")
print(f"\nFeedback Analysis:")
print(f"  Cases Actually Edited: {fb['edited_cases']}")
print(f"  Operator Confirmed (reviewed & agreed): {fb['operator_confirmed']}")
print(f"  Unreviewed Cases: {fb['unreviewed_cases']}")
print(f"  AI Acceptance Rate: {fb['acceptance_rate'] * 100:.1f}%")
print(f"  Edit Rate: {fb['edit_rate'] * 100:.1f}%")
print(f"  Review Rate: {fb['review_rate'] * 100:.1f}%")

# Display confidence scores
conf = analytics['confidence_scores']
print(f"\nAverage Confidence Scores:")
print(f"  Incident: {conf['incident']['average'] * 100:.1f}%")
print(f"  Severity: {conf['severity']['average'] * 100:.1f}%")
print(f"  Dispatch: {conf['dispatch']['average'] * 100:.1f}%")

# Display top 3 incident types
print(f"\nTop Incident Types:")
for incident_type, data in list(analytics['incident_types'].items())[:3]:
    print(f"  {incident_type}: {data['count']} ({data['percentage']}%)")

# Display language distribution
print(f"\nLanguage Distribution:")
for lang, data in analytics['languages'].items():
    print(f"  {lang}: {data['count']} ({data['percentage']}%)")

# Display severity distribution
print(f"\nSeverity Distribution:")
for severity, data in analytics['severity_levels'].items():
    print(f"  {severity}: {data['count']} ({data['percentage']}%)")

# Display dispatch units distribution
print(f"\nDispatch Units Distribution:")
for unit, data in analytics['dispatch_units'].items():
    print(f"  {unit}: {data['count']} ({data['percentage']}%)")
```

**Sample Output:**
```
Total Cases: 250

Feedback Analysis:
  Cases Actually Edited: 38
  Operator Confirmed (reviewed & agreed): 7
  Unreviewed Cases: 205
  AI Acceptance Rate: 84.8%
  Edit Rate: 15.2%
  Review Rate: 18.0%

Average Confidence Scores:
  Incident: 87.5%
  Severity: 85.2%
  Dispatch: 89.1%

Top Incident Types:
  MEDICAL: 100 (40.0%)
  POLICE: 80 (32.0%)
  FIRE: 50 (20.0%)

Language Distribution:
  en: 180 (72.0%)
  ar: 70 (28.0%)

Severity Distribution:
  CRITICAL: 30 (12.0%)
  HIGH: 80 (32.0%)
  MEDIUM: 100 (40.0%)
  LOW: 40 (16.0%)

Dispatch Units Distribution:
  AMBULANCE: 100 (40.0%)
  POLICE: 80 (32.0%)
  FIRE_DEPARTMENT: 50 (20.0%)
  FIRE_DEPARTMENT_HAZMAT: 20 (8.0%)
```

---

## Dashboard Visualization Ideas

### 1. KPI Cards
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Total Cases    │  │  Acceptance Rate│  │  Avg Confidence │
│      250        │  │      82%        │  │      87.6%      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 2. Pie Chart - Incident Types
```
     MEDICAL (40%)
       _____
      /     \
     |   •   |  POLICE (32%)
      \_____/
        |
    FIRE (20%)  OTHER (8%)
```

### 3. Bar Chart - Severity Levels
```
CRITICAL  ████████████░░░░░░░░░░░░ 12%
HIGH      ████████████████████████████████░░░░░░░░ 32%
MEDIUM    ████████████████████████████████████████ 40%
LOW       ████████████████░░░░░░░░░░░░░░░░░░░░░░░░ 16%
```

### 4. Donut Chart - Languages
```
      ┌─────┐
      │ 250 │
      │Cases│
      └─────┘
   EN: 72%  AR: 28%
```

### 5. Progress Bars - Confidence Scores
```
Incident   ████████████████████▌      87.5%
Severity   ████████████████████       85.2%
Dispatch   ████████████████████▊      89.1%
```

---

## React/Chart.js Example

```javascript
import React, { useEffect, useState } from 'react';
import { Pie, Bar, Doughnut } from 'react-chartjs-2';

function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/analytics')
      .then(res => res.json())
      .then(data => setAnalytics(data));
  }, []);

  if (!analytics) return <div>Loading...</div>;

  // Incident Types Pie Chart Data
  const incidentData = {
    labels: Object.keys(analytics.incident_types),
    datasets: [{
      data: Object.values(analytics.incident_types).map(v => v.count),
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
    }]
  };

  // Severity Levels Bar Chart Data
  const severityData = {
    labels: Object.keys(analytics.severity_levels),
    datasets: [{
      label: 'Cases by Severity',
      data: Object.values(analytics.severity_levels).map(v => v.count),
      backgroundColor: ['#FF4444', '#FF8844', '#FFCC44', '#44FF44']
    }]
  };

  return (
    <div className="dashboard">
      <h1>Emergency Dispatch Analytics</h1>

      {/* KPI Cards */}
      <div className="kpi-cards">
        <div className="card">
          <h3>Total Cases</h3>
          <h1>{analytics.total_cases}</h1>
        </div>
        <div className="card">
          <h3>Acceptance Rate</h3>
          <h1>{(analytics.feedback_analysis.acceptance_rate * 100).toFixed(1)}%</h1>
        </div>
        <div className="card">
          <h3>Avg Confidence</h3>
          <h1>
            {(
              (analytics.confidence_scores.incident.average +
               analytics.confidence_scores.severity.average +
               analytics.confidence_scores.dispatch.average) / 3 * 100
            ).toFixed(1)}%
          </h1>
        </div>
      </div>

      {/* Charts */}
      <div className="charts">
        <div className="chart">
          <h3>Incident Types</h3>
          <Pie data={incidentData} />
        </div>
        <div className="chart">
          <h3>Severity Levels</h3>
          <Bar data={severityData} />
        </div>
      </div>
    </div>
  );
}

export default AnalyticsDashboard;
```

---

## Use Cases

### 1. Operations Dashboard
Monitor daily operations and system performance:
- Total cases handled today/this week/this month
- AI acceptance rate trends
- Current workload distribution

### 2. Performance Monitoring
Track AI model performance:
- Confidence score trends over time
- Cases requiring human review
- Feedback patterns (when does AI need correction?)

### 3. Resource Planning
Allocate resources based on data:
- Most common incident types
- Language requirements
- Severity distribution patterns

### 4. Quality Assurance
Ensure system quality:
- Low confidence cases for review
- Edit rate by incident type
- Operator feedback patterns

### 5. Reporting
Generate reports for stakeholders:
- Monthly statistics
- Performance metrics
- Trend analysis

---

## Best Practices

### 1. Caching
For high-traffic dashboards, consider caching:
```python
import time
from functools import lru_cache

@lru_cache(maxsize=1)
def get_cached_analytics(timestamp):
    """Cache analytics for 5 minutes."""
    return requests.get("http://localhost:8000/api/analytics").json()

# Use with 5-minute intervals
analytics = get_cached_analytics(int(time.time() / 300))
```

### 2. Periodic Refresh
Update dashboard every 30-60 seconds:
```javascript
useEffect(() => {
  const interval = setInterval(() => {
    fetchAnalytics();
  }, 30000); // 30 seconds

  return () => clearInterval(interval);
}, []);
```

### 3. Error Handling
Always handle potential errors:
```python
try:
    response = requests.get("http://localhost:8000/api/analytics")
    response.raise_for_status()
    analytics = response.json()
except requests.RequestException as e:
    print(f"Error fetching analytics: {e}")
    # Use cached data or show error message
```

---

## Testing

```bash
# Test endpoint
curl http://localhost:8000/api/analytics

# Pretty print JSON
curl http://localhost:8000/api/analytics | python -m json.tool

# Save to file
curl http://localhost:8000/api/analytics > analytics.json
```

---

## Summary

The analytics endpoint provides all the metrics you need for:
- ✅ Monitoring AI performance (confidence scores, acceptance rates)
- ✅ Understanding workload (incident types, severity distribution)
- ✅ Resource planning (language distribution)
- ✅ Building dashboards (all metrics with counts AND percentages)
- ✅ Decision making (clear, easy-to-use numbers and ratios)

All data is optimized for dashboard visualization with both raw counts and calculated percentages.
