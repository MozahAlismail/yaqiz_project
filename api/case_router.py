"""Case Management Router"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["cases"])


@router.get("/get-case/{case_id}")
async def get_case(case_id: str) -> Dict[str, Any]:
    """Retrieve a case by ID."""
    from main import get_main_controller
    controller = get_main_controller()
    
    result = controller.get_case(case_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result
