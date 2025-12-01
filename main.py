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

# Import routers
from api.audio_router import router as audio_router
from api.feedback_router import router as feedback_router
from api.case_router import router as case_router
from api.retrain_router import router as retrain_router
from api.health_router import router as health_router

# Initialize database
from data.init_db import initialize_databases

# Global instances
_config = None
_main_controller = None
_rlhf_trainer = None


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
    global _config, _main_controller, _rlhf_trainer
    
    # Load configuration
    _config = load_config()
    
    # Setup logging
    setup_logging(_config)
    logger.info("Starting AI Emergency Dispatch Assistant")
    
    # Initialize databases
    initialize_databases()
    
    # Create models
    stt_model = create_stt_model(_config)
    language_model = create_language_model(_config)
    incident_classifier = create_incident_classifier(_config)
    severity_classifier = create_severity_classifier(_config)
    dispatch_classifier = create_dispatch_classifier(_config)
    _rlhf_trainer = create_rlhf_trainer(_config)
    
    # Create agents
    stt_agent = STTAgent(stt_model)
    language_agent = LanguageDetectionAgent(language_model)
    incident_agent = IncidentAgent(incident_classifier)
    severity_agent = SeverityAgent(severity_classifier)
    dispatch_agent = DispatchAgent(dispatch_classifier)
    self_eval_agent = SelfEvaluationAgent(_config)
    
    # Create agent controller
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
    
    logger.info("System initialization complete")


def get_main_controller():
    """Get main controller instance."""
    return _main_controller


def get_rlhf_trainer():
    """Get RLHF trainer instance."""
    return _rlhf_trainer


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
