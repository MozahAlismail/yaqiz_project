"""Model Retraining Router"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/api", tags=["training"])


@router.post("/retrain-model")
async def retrain_model() -> Dict[str, Any]:
    """Trigger RLHF retraining based on feedback."""
    from main import get_rlhf_trainer
    trainer = get_rlhf_trainer()
    
    result = trainer.train()
    return result
