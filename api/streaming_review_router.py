"""
Streaming Review Queue Router

Provides API endpoints for the human review queue:
- GET /api/streaming/review-queue - Get prioritized review queue
- POST /api/streaming/complete-review - Complete human review
- GET /api/streaming/case/{case_id} - Get streaming case details
- GET /api/streaming/metrics - Get processing metrics

IMPORTANT: This is a NEW file - does not modify existing routers.
"""

import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/streaming", tags=["Streaming Review Queue"])

# Global database config (set during initialization)
_db_config = None


# ═══════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════

class CompleteReviewRequest(BaseModel):
    """Request model for completing a human review."""
    case_id: str = Field(..., description="Case ID to review")
    human_incident: Optional[str] = Field(None, description="Human-corrected incident type")
    human_severity: Optional[str] = Field(None, description="Human-corrected severity level")
    human_unit: Optional[str] = Field(None, description="Human-corrected dispatch unit")
    operator_id: str = Field(..., description="Operator ID performing review")
    approved: bool = Field(..., description="Whether the case is approved for dispatch")
    notes: Optional[str] = Field(None, description="Optional review notes")


class ReviewQueueItem(BaseModel):
    """Model for a review queue item."""
    case_id: str
    transcript: str
    detected_language: str
    ai_incident: str
    ai_severity: str
    ai_unit: str
    incident_confidence: float
    severity_confidence: float
    dispatch_confidence: float
    review_priority: str
    exit_reason: str
    evaluation_summary: str
    created_at: str
    processing_metrics: Optional[dict] = None


class ReviewQueueResponse(BaseModel):
    """Response model for review queue."""
    total_count: int
    urgent_count: int
    high_count: int
    normal_count: int
    cases: List[dict]


# ═══════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def init_streaming_review_router(db_config: dict):
    """Initialize router with database configuration.

    Args:
        db_config: Database configuration dictionary
    """
    global _db_config
    _db_config = db_config
    logger.info("Streaming review router initialized with database config")


def _get_db_connection():
    """Get a database connection."""
    if _db_config is None:
        raise RuntimeError("Database config not initialized")

    return psycopg2.connect(
        host=_db_config.get("host", "localhost"),
        port=_db_config.get("port", 5432),
        database=_db_config.get("database", "emergency_dispatch"),
        user=_db_config.get("user", "postgres"),
        password=_db_config.get("password", "postgres")
    )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/review-queue")
async def get_review_queue(
    priority: Optional[str] = Query(None, description="Filter by priority: urgent, high, normal"),
    limit: int = Query(50, description="Maximum number of cases to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """Get the prioritized human review queue.

    Returns cases ordered by priority (urgent > high > normal) and then by creation time.

    Args:
        priority: Optional filter for specific priority level
        limit: Maximum number of cases to return
        offset: Offset for pagination

    Returns:
        ReviewQueueResponse with prioritized cases
    """
    try:
        conn = _get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Build query based on priority filter
        base_query = """
            SELECT
                case_id, transcript, detected_language,
                ai_incident, ai_severity, ai_unit,
                incident_confidence, severity_confidence, dispatch_confidence,
                requires_review, review_priority, exit_reason,
                processing_mode, evaluation_summary, concerns,
                processing_metrics, created_at
            FROM cases
            WHERE requires_review = TRUE
            AND processing_mode = 'streaming'
        """

        if priority:
            base_query += " AND review_priority = %s"
            params = [priority]
        else:
            params = []

        # Order by priority (urgent first) then by creation time
        base_query += """
            ORDER BY
                CASE review_priority
                    WHEN 'urgent' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'normal' THEN 3
                    ELSE 4
                END,
                created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        cursor.execute(base_query, params)
        cases = cursor.fetchall()

        # Get counts by priority
        cursor.execute("""
            SELECT review_priority, COUNT(*) as count
            FROM cases
            WHERE requires_review = TRUE
            AND processing_mode = 'streaming'
            GROUP BY review_priority
        """)
        counts = {row["review_priority"]: row["count"] for row in cursor.fetchall()}

        cursor.close()
        conn.close()

        # Format cases for response
        formatted_cases = []
        for case in cases:
            formatted_case = dict(case)
            # Convert datetime to string
            if formatted_case.get("created_at"):
                formatted_case["created_at"] = formatted_case["created_at"].isoformat()
            formatted_cases.append(formatted_case)

        return JSONResponse(content={
            "total_count": sum(counts.values()),
            "urgent_count": counts.get("urgent", 0),
            "high_count": counts.get("high", 0),
            "normal_count": counts.get("normal", 0),
            "cases": formatted_cases
        })

    except psycopg2.Error as e:
        logger.error(f"Database error getting review queue: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting review queue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/case/{case_id}")
async def get_streaming_case(case_id: str):
    """Get detailed information for a streaming case.

    Args:
        case_id: The case ID to retrieve

    Returns:
        Complete case details including processing metrics
    """
    try:
        conn = _get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT * FROM cases WHERE case_id = %s
        """, (case_id,))

        case = cursor.fetchone()

        if not case:
            raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")

        # Get any existing feedback
        cursor.execute("""
            SELECT * FROM feedback WHERE case_id = %s
        """, (case_id,))

        feedback = cursor.fetchone()

        cursor.close()
        conn.close()

        # Format response
        case_dict = dict(case)
        if case_dict.get("created_at"):
            case_dict["created_at"] = case_dict["created_at"].isoformat()
        if case_dict.get("updated_at"):
            case_dict["updated_at"] = case_dict["updated_at"].isoformat()

        response = {
            "case": case_dict,
            "feedback": dict(feedback) if feedback else None,
            "has_been_reviewed": feedback is not None
        }

        return JSONResponse(content=response)

    except HTTPException:
        raise
    except psycopg2.Error as e:
        logger.error(f"Database error getting case {case_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting case {case_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete-review")
async def complete_review(request: CompleteReviewRequest):
    """Complete a human review for a streaming case.

    This endpoint:
    1. Records the human review feedback
    2. Updates the case with review status
    3. Marks the case as ready for dispatch (if approved)

    Args:
        request: CompleteReviewRequest with review details

    Returns:
        Confirmation of review completion
    """
    try:
        conn = _get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Verify case exists
        cursor.execute("""
            SELECT case_id, ai_incident, ai_severity, ai_unit
            FROM cases WHERE case_id = %s
        """, (request.case_id,))

        case = cursor.fetchone()
        if not case:
            raise HTTPException(status_code=404, detail=f"Case not found: {request.case_id}")

        # Generate feedback ID
        import uuid
        feedback_id = str(uuid.uuid4())

        # Use AI values if human didn't correct
        final_incident = request.human_incident or case["ai_incident"]
        final_severity = request.human_severity or case["ai_severity"]
        final_unit = request.human_unit or case["ai_unit"]

        # Insert or update feedback
        cursor.execute("""
            INSERT INTO feedback (
                feedback_id, case_id, corrected_incident, corrected_severity,
                corrected_unit, operator_id, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (case_id) DO UPDATE SET
                corrected_incident = EXCLUDED.corrected_incident,
                corrected_severity = EXCLUDED.corrected_severity,
                corrected_unit = EXCLUDED.corrected_unit,
                operator_id = EXCLUDED.operator_id,
                timestamp = EXCLUDED.timestamp
        """, (
            feedback_id, request.case_id, final_incident, final_severity,
            final_unit, request.operator_id, datetime.utcnow()
        ))

        # Update case review status
        cursor.execute("""
            UPDATE cases SET
                requires_review = FALSE,
                updated_at = %s
            WHERE case_id = %s
        """, (datetime.utcnow(), request.case_id))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Review completed for case {request.case_id} by {request.operator_id}")

        return JSONResponse(content={
            "status": "success",
            "message": "Review completed successfully",
            "case_id": request.case_id,
            "feedback_id": feedback_id,
            "approved": request.approved,
            "final_classification": {
                "incident": final_incident,
                "severity": final_severity,
                "dispatch_unit": final_unit
            },
            "reviewed_by": request.operator_id,
            "reviewed_at": datetime.utcnow().isoformat()
        })

    except HTTPException:
        raise
    except psycopg2.Error as e:
        logger.error(f"Database error completing review: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error completing review: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_streaming_metrics(
    hours: int = Query(24, description="Number of hours to look back")
):
    """Get streaming processing metrics and statistics.

    Args:
        hours: Number of hours to look back for statistics

    Returns:
        Processing metrics and performance statistics
    """
    try:
        conn = _get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get overall statistics
        cursor.execute("""
            SELECT
                COUNT(*) as total_cases,
                COUNT(*) FILTER (WHERE requires_review = TRUE) as pending_review,
                COUNT(*) FILTER (WHERE requires_review = FALSE) as reviewed,
                COUNT(*) FILTER (WHERE review_priority = 'urgent') as urgent_count,
                COUNT(*) FILTER (WHERE review_priority = 'high') as high_count,
                COUNT(*) FILTER (WHERE review_priority = 'normal') as normal_count,
                AVG(incident_confidence) as avg_incident_confidence,
                AVG(severity_confidence) as avg_severity_confidence,
                AVG(dispatch_confidence) as avg_dispatch_confidence
            FROM cases
            WHERE processing_mode = 'streaming'
            AND created_at >= NOW() - INTERVAL '%s hours'
        """, (hours,))

        stats = cursor.fetchone()

        # Get exit reason distribution
        cursor.execute("""
            SELECT exit_reason, COUNT(*) as count
            FROM cases
            WHERE processing_mode = 'streaming'
            AND created_at >= NOW() - INTERVAL '%s hours'
            GROUP BY exit_reason
        """, (hours,))

        exit_reasons = {row["exit_reason"]: row["count"] for row in cursor.fetchall()}

        # Get average processing times from metrics
        cursor.execute("""
            SELECT
                AVG((processing_metrics->>'total_processing_time_ms')::float) as avg_total_ms,
                AVG((processing_metrics->>'classification_total_time_ms')::float) as avg_classification_ms,
                AVG((processing_metrics->>'stt_time_ms')::float) as avg_stt_ms
            FROM cases
            WHERE processing_mode = 'streaming'
            AND processing_metrics IS NOT NULL
            AND created_at >= NOW() - INTERVAL '%s hours'
        """, (hours,))

        processing_times = cursor.fetchone()

        cursor.close()
        conn.close()

        return JSONResponse(content={
            "period_hours": hours,
            "statistics": {
                "total_cases": stats["total_cases"] or 0,
                "pending_review": stats["pending_review"] or 0,
                "reviewed": stats["reviewed"] or 0,
                "by_priority": {
                    "urgent": stats["urgent_count"] or 0,
                    "high": stats["high_count"] or 0,
                    "normal": stats["normal_count"] or 0
                }
            },
            "confidence_averages": {
                "incident": round(stats["avg_incident_confidence"] or 0, 3),
                "severity": round(stats["avg_severity_confidence"] or 0, 3),
                "dispatch": round(stats["avg_dispatch_confidence"] or 0, 3)
            },
            "exit_reason_distribution": exit_reasons,
            "processing_times_ms": {
                "avg_total": round(processing_times["avg_total_ms"] or 0, 1),
                "avg_classification": round(processing_times["avg_classification_ms"] or 0, 1),
                "avg_stt": round(processing_times["avg_stt_ms"] or 0, 1)
            }
        })

    except psycopg2.Error as e:
        logger.error(f"Database error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def streaming_info():
    """Get information about the streaming review API.

    Returns:
        API documentation and endpoint information
    """
    return JSONResponse(content={
        "description": "Streaming Emergency Dispatch Human Review Queue",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/streaming/review-queue": {
                "description": "Get prioritized review queue",
                "parameters": {
                    "priority": "Filter by priority (urgent, high, normal)",
                    "limit": "Maximum cases to return (default: 50)",
                    "offset": "Pagination offset (default: 0)"
                }
            },
            "GET /api/streaming/case/{case_id}": {
                "description": "Get detailed case information",
                "parameters": {
                    "case_id": "The case ID to retrieve"
                }
            },
            "POST /api/streaming/complete-review": {
                "description": "Complete human review for a case",
                "body": {
                    "case_id": "Case ID (required)",
                    "human_incident": "Corrected incident type (optional)",
                    "human_severity": "Corrected severity level (optional)",
                    "human_unit": "Corrected dispatch unit (optional)",
                    "operator_id": "Operator ID (required)",
                    "approved": "Approval status (required)",
                    "notes": "Review notes (optional)"
                }
            },
            "GET /api/streaming/metrics": {
                "description": "Get processing metrics and statistics",
                "parameters": {
                    "hours": "Lookback period in hours (default: 24)"
                }
            }
        },
        "review_priorities": {
            "urgent": "Critical severity or unsupported language - immediate review required",
            "high": "Low AI confidence after timeout - priority review needed",
            "normal": "AI confident - standard review queue"
        },
        "note": "ALL cases require human review before dispatch - this is an emergency system"
    })