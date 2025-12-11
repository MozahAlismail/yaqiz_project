"""Analytics Router - Dashboard metrics and statistics"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics")
async def get_analytics() -> Dict[str, Any]:
    """
    Retrieve comprehensive analytics for dashboard.

    Returns comprehensive metrics including:
    - **Feedback Analysis**: Edited vs correct cases with edit/acceptance rates
    - **Confidence Scores**: Average AI confidence scores for incident, severity, and dispatch
    - **Incident Types**: Distribution of incident types (FIRE, MEDICAL, POLICE, etc.)
    - **Languages**: Distribution of detected languages (en, ar, etc.)
    - **Severity Levels**: Distribution of severity levels (CRITICAL, HIGH, MEDIUM, LOW)
    - **Dispatch Units**: Distribution of dispatch units (FIRE_DEPARTMENT, AMBULANCE, POLICE, etc.)

    All metrics include both counts and percentages for easy dashboard visualization.

    Example Response:
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
        "incident": {"average": 0.8745, "total_cases": 250},
        "severity": {"average": 0.8523, "total_cases": 250},
        "dispatch": {"average": 0.8912, "total_cases": 250}
      },
      "incident_types": {
        "FIRE": {"count": 50, "percentage": 20.0},
        "MEDICAL": {"count": 100, "percentage": 40.0},
        "POLICE": {"count": 80, "percentage": 32.0}
      },
      "languages": {
        "en": {"count": 180, "percentage": 72.0},
        "ar": {"count": 70, "percentage": 28.0}
      },
      "severity_levels": {
        "CRITICAL": {"count": 30, "percentage": 12.0},
        "HIGH": {"count": 80, "percentage": 32.0},
        "MEDIUM": {"count": 100, "percentage": 40.0},
        "LOW": {"count": 40, "percentage": 16.0}
      },
      "dispatch_units": {
        "AMBULANCE": {"count": 100, "percentage": 40.0},
        "POLICE": {"count": 80, "percentage": 32.0},
        "FIRE_DEPARTMENT": {"count": 50, "percentage": 20.0},
        "FIRE_DEPARTMENT_HAZMAT": {"count": 20, "percentage": 8.0}
      }
    }
    ```

    Returns:
        Dictionary with comprehensive analytics data
    """
    from main import get_main_controller
    controller = get_main_controller()

    result = controller.get_analytics()

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result
