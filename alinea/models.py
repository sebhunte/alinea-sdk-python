"""
Core data models for the Alinea SDK.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union, Literal
from datetime import datetime


@dataclass
class Intention:
    """Represents an intention from an agent to perform an action."""
    agent_id: str
    action: str
    affected_resources: List[str]
    context: Dict[str, Any]
    intention_id: Optional[str] = None
    timestamp: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class ActionResult:
    """Result of executing an intention."""
    intention_id: str
    outcome: Literal["success", "failure"]
    reason: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    timestamp: Optional[str] = None


@dataclass
class PatternConfidence:
    """Confidence metrics for learned patterns."""
    pattern_id: str
    confidence_score: float
    sample_count: int
    last_updated: str
    pattern_type: str


@dataclass
class AdaptationMetrics:
    """Metrics about system adaptation and learning."""
    total_patterns: int
    high_confidence_patterns: int
    learning_rate: float
    surprise_events: int
    adaptation_score: float
    last_updated: str


@dataclass
class MigrationStatus:
    """Status of pattern migration and system updates."""
    migration_id: str
    status: Literal["pending", "in_progress", "completed", "failed"]
    progress: float
    affected_agents: List[str]
    estimated_completion: Optional[str] = None
    error_details: Optional[str] = None


@dataclass
class CausalNode:
    """A node in a causal analysis path."""
    agent_id: str
    action: str
    timestamp: str
    resource_changes: Dict[str, Any]
    causal_strength: float


@dataclass
class CausalPath:
    """A complete causal analysis path."""
    target_event: str
    path: List[CausalNode]
    confidence: float
    total_impact_score: float


@dataclass
class ImpactAnalysis:
    """Analysis of the impact of an agent's change."""
    source_agent: str
    source_action: str
    affected_agents: List[str]
    impact_score: float
    impact_details: Dict[str, Any]
    propagation_time: float


@dataclass
class CounterfactualAnalysis:
    """What-if analysis for alternative timelines."""
    original_event: str
    counterfactual_scenario: str
    probability_difference: float
    outcome_changes: Dict[str, Any]
    confidence: float


@dataclass
class WorldSnapshot:
    """Snapshot of world state at a specific time."""
    hlc_time: str
    resources: Dict[str, Any]
    active_agents: List[str]
    resource_locks: Dict[str, str]
    snapshot_id: str
    creation_timestamp: str


@dataclass
class MemoryPattern:
    """A learned memory pattern."""
    pattern_id: str
    pattern_type: str
    trigger_conditions: Dict[str, Any]
    expected_outcomes: Dict[str, Any]
    confidence: float
    usage_count: int
    last_accessed: str
    surprise_events: List[Dict[str, Any]]


@dataclass
class APIResponse:
    """Standard API response wrapper."""
    success: bool
    data: Any
    error: Optional[str] = None
    timestamp: Optional[str] = None
    request_id: Optional[str] = None
