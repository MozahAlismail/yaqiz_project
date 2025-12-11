"""
AI Emergency Dispatch Assistant - Main Application

FastAPI application that coordinates all agents and provides REST API endpoints.
"""

import logging
from pathlib import Path
import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Import models
from models.stt_model import create_stt_model
from models.language_model import create_language_model
from models.incident_classifier import create_incident_classifier
from models.severity_classifier import create_severity_classifier
from models.dispatch_classifier import create_dispatch_classifier
from models.rlhf_trainer import create_rlhf_trainer
from models.translation_model import create_translation_model

# Import agents
from agents.stt_agent import STTAgent
from agents.language_detection_agent import LanguageDetectionAgent
from agents.incident_agent import IncidentAgent
from agents.severity_agent import SeverityAgent
from agents.dispatch_agent import DispatchAgent
from agents.self_eval_agent import SelfEvaluationAgent

# Import controllers
from controllers.agent_controller import AgentController
from controllers.main_controller import MainController
from controllers.realtime_audio_controller import realtimeAudioController

# Import LangGraph workflow
from graph.workflow import create_emergency_graph, get_emergency_graph

# Import routers
from api.audio_router import router as audio_router
from api.feedback_router import router as feedback_router
from api.case_router import router as case_router
from api.retrain_router import router as retrain_router
from api.health_router import router as health_router
from api.analytics_router import router as analytics_router
from api.realtime_audio_router import router as realtime_audio_router
from api.websocket_audio_router import router as websocket_audio_router

# Import services
from services.realtime_audio_service import create_realtime_audio_service
from services.websocket_audio_service import create_websocket_audio_service

# Initialize database
from data.init_db import initialize_databases

# Global instances
_config = None
_main_controller = None
_rlhf_trainer = None
_realtime_audio_service = None
_realtime_audio_controller = None
_websocket_audio_service = None
_translation_model = None
_incident_classifier = None
_severity_classifier = None
_dispatch_classifier = None
_emergency_graph = None
_language_model = None
_stt_model = None


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def setup_logging(config: dict):
    """Setup logging configuration."""
    log_config = config.get("logging", {})
    logger.add(
        log_config.get("log_file", "logs/app.log"),
        rotation=log_config.get("rotation", "500 MB"),
        retention=log_config.get("retention", "10 days"),
        level=log_config.get("level", "INFO")
    )


def initialize_system():
    """Initialize all system components."""
    global _config, _main_controller, _rlhf_trainer, _realtime_audio_service
    global _realtime_audio_controller, _websocket_audio_service, _translation_model
    global _incident_classifier, _severity_classifier, _dispatch_classifier
    global _emergency_graph, _language_model, _stt_model

    # Load configuration
    _config = load_config()

    # Setup logging
    setup_logging(_config)
    logger.info("Starting AI Emergency Dispatch Assistant")

    # Initialize databases
    initialize_databases()

    # Create models (store in globals for graph access)
    _stt_model = create_stt_model(_config)
    _language_model = create_language_model(_config)
    _incident_classifier = create_incident_classifier(_config)
    _severity_classifier = create_severity_classifier(_config)
    _dispatch_classifier = create_dispatch_classifier(_config)
    _rlhf_trainer = create_rlhf_trainer(_config)
    _translation_model = create_translation_model(_config)

    # Initialize LangGraph emergency workflow
    logger.info("Initializing LangGraph emergency dispatch workflow")
    _emergency_graph = create_emergency_graph(
        stt_model=_stt_model,
        language_model=_language_model,
        incident_classifier=_incident_classifier,
        severity_classifier=_severity_classifier,
        dispatch_classifier=_dispatch_classifier,
        config=_config,
        enable_checkpointing=_config.get("hitl", {}).get("enabled", True)
    )
    logger.info("LangGraph emergency dispatch workflow initialized")

    # Create agents (still needed for legacy support and other services)
    stt_agent = STTAgent(_stt_model)
    language_agent = LanguageDetectionAgent(_language_model)
    incident_agent = IncidentAgent(_incident_classifier)
    severity_agent = SeverityAgent(_severity_classifier)
    dispatch_agent = DispatchAgent(_dispatch_classifier)
    self_eval_agent = SelfEvaluationAgent(_config)

    # Create agent controller (now uses LangGraph internally)
    agent_controller = AgentController(
        stt_agent=stt_agent,
        language_agent=language_agent,
        incident_agent=incident_agent,
        severity_agent=severity_agent,
        dispatch_agent=dispatch_agent,
        self_eval_agent=self_eval_agent
    )

    # Create main controller
    _main_controller = MainController(
        agent_controller=agent_controller,
        db_config=_config.get("database", {})
    )

    # Create realtime audio service with translation model
    _realtime_audio_service = create_realtime_audio_service(
        config=_config,
        translation_model=_translation_model
    )

    # Create realtime audio controller
    _realtime_audio_controller = realtimeAudioController(
        realtime_audio_service=_realtime_audio_service,
        incident_classifier=_incident_classifier,
        severity_classifier=_severity_classifier,
        dispatch_classifier=_dispatch_classifier,
        db_config=_config.get("database", {})
    )

    # Create websocket audio service
    _websocket_audio_service = create_websocket_audio_service(
        config=_config,
        translation_model=_translation_model
    )

    # Initialize websocket audio router with service and classifiers
    from api.websocket_audio_router import init_websocket_audio_service
    init_websocket_audio_service(
        service=_websocket_audio_service,
        incident_clf=_incident_classifier,
        severity_clf=_severity_classifier,
        dispatch_clf=_dispatch_classifier
    )

    logger.info("System initialization complete")


def get_main_controller():
    """Get main controller instance."""
    return _main_controller


def get_rlhf_trainer():
    """Get RLHF trainer instance."""
    return _rlhf_trainer


def get_realtime_audio_service():
    """Get realtime audio service instance."""
    return _realtime_audio_service


def get_incident_classifier():
    """Get incident classifier instance."""
    return _incident_classifier


def get_severity_classifier():
    """Get severity classifier instance."""
    return _severity_classifier


def get_dispatch_classifier():
    """Get dispatch classifier instance."""
    return _dispatch_classifier


def get_realtime_audio_controller():
    """Get realtime audio controller instance."""
    return _realtime_audio_controller


def get_translation_model():
    """Get translation model instance."""
    return _translation_model


def get_websocket_audio_service():
    """Get websocket audio service instance."""
    return _websocket_audio_service


def get_emergency_graph_instance():
    """Get the compiled LangGraph emergency dispatch workflow."""
    return _emergency_graph


def get_stt_model():
    """Get STT model instance."""
    return _stt_model


def get_language_model():
    """Get language detection model instance."""
    return _language_model


# Create FastAPI app
app = FastAPI(
    title="AI Emergency Dispatch Assistant",
    description="Multilingual AI system for analyzing emergency calls",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(audio_router)
app.include_router(feedback_router)
app.include_router(case_router)
app.include_router(retrain_router)
app.include_router(health_router)
app.include_router(analytics_router)
app.include_router(realtime_audio_router)
app.include_router(websocket_audio_router)


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    initialize_system()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Emergency Dispatch Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    config = load_config()
    app_config = config.get("app", {})
    
    uvicorn.run(
        "main:app",
        host=app_config.get("host", "0.0.0.0"),
        port=app_config.get("port", 8000),
        reload=app_config.get("debug", False)
    )
