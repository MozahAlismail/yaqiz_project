"""Health Check Router"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Emergency Dispatch Assistant",
        "version": "1.0.0"
    }
