"""Feedback Router"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api", tags=["feedback"])


class FeedbackRequest(BaseModel):
    case_id: str
    corrected_incident: Optional[str] = None
    corrected_severity: Optional[str] = None
    corrected_unit: Optional[str] = None
    operator_id: Optional[str] = "unknown"


@router.post("/operator-feedback")
async def submit_feedback(feedback: FeedbackRequest) -> Dict[str, Any]:
    """Submit operator feedback for a case."""
    from main import get_main_controller
    controller = get_main_controller()
    
    result = controller.submit_feedback(feedback.dict())
    return result
