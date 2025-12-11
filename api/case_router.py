"""Case Management Router"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["cases"])


@router.get("/case/{case_id}")
async def get_case(case_id: str) -> Dict[str, Any]:
    """
    Retrieve a specific case by ID.

    Args:
        case_id: UUID of the case to retrieve

    Returns:
        Case details including transcript, AI predictions, and confidence scores
    """
    from main import get_main_controller
    controller = get_main_controller()

    result = controller.get_case(case_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/cases")
async def get_all_cases(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of cases to return"),
    offset: int = Query(default=0, ge=0, description="Number of cases to skip")
) -> Dict[str, Any]:
    """
    Retrieve all cases with pagination.

    Returns all emergency call cases with AI analysis results.
    Results are ordered by creation time (newest first).

    Args:
        limit: Maximum number of cases to return (1-1000, default: 100)
        offset: Number of cases to skip for pagination (default: 0)

    Returns:
        Dictionary containing:
        - total: Total number of cases in database
        - limit: Applied limit
        - offset: Applied offset
        - count: Number of cases returned
        - cases: List of case objects

    Example:
        GET /api/cases?limit=50&offset=0
    """
    from main import get_main_controller
    controller = get_main_controller()

    result = controller.get_all_cases(limit=limit, offset=offset)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


# Keep backward compatibility with old endpoint
# @router.get("/get-case/{case_id}")
# async def get_case_legacy(case_id: str) -> Dict[str, Any]:
#     """
#     [DEPRECATED] Use /api/case/{case_id} instead.

#     Legacy endpoint for backward compatibility.
#     """
#     return await get_case(case_id)


# @router.put("/case/{case_id}")
# async def update_case(case_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Update a case's information.

#     You can update any of the following fields:
#     - transcript
#     - detected_language
#     - language_confidence
#     - ai_incident
#     - ai_severity
#     - ai_unit
#     - incident_confidence
#     - severity_confidence
#     - dispatch_confidence
#     - requires_review

#     Args:
#         case_id: UUID of the case to update
#         update_data: Dictionary with fields to update

#     Returns:
#         Success status and list of updated fields

#     Example:
#         PUT /api/case/{case_id}
#         {
#           "ai_incident": "FIRE",
#           "requires_review": false
#         }
#     """
#     from main import get_main_controller
#     controller = get_main_controller()

#     result = controller.update_case(case_id, update_data)

#     if "error" in result:
#         if result["error"] == "Case not found":
#             raise HTTPException(status_code=404, detail=result["error"])
#         raise HTTPException(status_code=400, detail=result["error"])

#     return result


# @router.delete("/case/{case_id}")
# async def delete_case(case_id: str) -> Dict[str, Any]:
#     """
#     Delete a case by ID.

#     ⚠️ WARNING: This will also delete any associated feedback due to CASCADE constraint.

#     Args:
#         case_id: UUID of the case to delete

#     Returns:
#         Success status and confirmation message

#     Example:
#         DELETE /api/case/{case_id}
#     """
#     from main import get_main_controller
#     controller = get_main_controller()

#     result = controller.delete_case(case_id)

#     if "error" in result:
#         raise HTTPException(status_code=404, detail=result["error"])

#     return result
