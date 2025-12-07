"""Feedback Router"""

from fastapi import APIRouter, HTTPException, Query
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
    """
    Submit operator feedback for a case.

    This endpoint allows operators to submit corrections for AI predictions,
    which will be used for model improvement (RLHF).
    """
    from main import get_main_controller
    controller = get_main_controller()

    result = controller.submit_feedback(feedback.dict())
    return result


@router.get("/feedback/{feedback_id}")
async def get_feedback(feedback_id: str) -> Dict[str, Any]:
    """
    Retrieve a specific feedback by ID.

    Args:
        feedback_id: UUID of the feedback to retrieve

    Returns:
        Feedback details including corrections and operator information
    """
    from main import get_main_controller
    controller = get_main_controller()

    result = controller.get_feedback(feedback_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/feedbacks")
async def get_all_feedbacks(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of feedbacks to return"),
    offset: int = Query(default=0, ge=0, description="Number of feedbacks to skip")
) -> Dict[str, Any]:
    """
    Retrieve all feedbacks with pagination.

    Returns feedbacks with associated case information (transcript, AI predictions).
    Results are ordered by timestamp (newest first).

    Args:
        limit: Maximum number of feedbacks to return (1-1000, default: 100)
        offset: Number of feedbacks to skip for pagination (default: 0)

    Returns:
        Dictionary containing:
        - total: Total number of feedbacks in database
        - limit: Applied limit
        - offset: Applied offset
        - count: Number of feedbacks returned
        - feedbacks: List of feedback objects with case details

    Example:
        GET /api/feedbacks?limit=50&offset=0
    """
    from main import get_main_controller
    controller = get_main_controller()

    result = controller.get_all_feedbacks(limit=limit, offset=offset)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@router.put("/feedback/{feedback_id}")
async def update_feedback(feedback_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a feedback's information.

    You can update any of the following fields:
    - corrected_incident
    - corrected_severity
    - corrected_unit
    - operator_id

    Note: The timestamp will be automatically updated.

    Args:
        feedback_id: UUID of the feedback to update
        update_data: Dictionary with fields to update

    Returns:
        Success status and list of updated fields

    Example:
        PUT /api/feedback/{feedback_id}
        {
          "corrected_incident": "MEDICAL",
          "corrected_severity": "HIGH"
        }
    """
    from main import get_main_controller
    controller = get_main_controller()

    result = controller.update_feedback(feedback_id, update_data)

    if "error" in result:
        if result["error"] == "Feedback not found":
            raise HTTPException(status_code=404, detail=result["error"])
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# @router.delete("/feedback/{feedback_id}")
# async def delete_feedback(feedback_id: str) -> Dict[str, Any]:
    """
    Delete a feedback by ID.

    This will only delete the feedback record. The associated case will remain.

    Args:
        feedback_id: UUID of the feedback to delete

    Returns:
        Success status and confirmation message

    Example:
        DELETE /api/feedback/{feedback_id}
    """
    from main import get_main_controller
    controller = get_main_controller()

    result = controller.delete_feedback(feedback_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result
