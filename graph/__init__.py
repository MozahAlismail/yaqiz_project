"""
LangGraph-based Emergency Dispatch Workflow

This module provides a LangGraph implementation for the emergency dispatch
multi-agent pipeline, replacing the sequential AgentController orchestration
with a graph-based workflow that supports:
- Stateful execution with TypedDict state management
- Conditional routing based on confidence scores
- Checkpointing for Human-in-the-Loop (HITL) workflows
- Parallel node execution where applicable
"""

from graph.state import EmergencyState
from graph.workflow import create_emergency_graph, get_emergency_graph

__all__ = [
    "EmergencyState",
    "create_emergency_graph",
    "get_emergency_graph",
]
