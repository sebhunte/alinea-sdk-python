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


# Forward Simulation Models
@dataclass
class SimulationResult:
    """Result of forward simulation analysis."""
    agent_id: str
    action: str
    resources: List[str]
    risk_score: float  # 0.0 to 1.0
    safe_to_proceed: bool
    predicted_conflicts: List[Dict[str, Any]]
    alternative_timing: Optional[str] = None
    recommendations: List[str] = None
    confidence: float = 0.0  # 0.0 to 1.0
    simulation_timestamp: Optional[str] = None
    look_ahead_minutes: int = 5

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        if self.simulation_timestamp is None:
            self.simulation_timestamp = datetime.now().isoformat()


@dataclass
class WhatIfAnalysis:
    """Result of natural language what-if analysis."""
    question: str
    analysis: str
    predicted_outcomes: List[Dict[str, Any]]
    risk_factors: List[str]
    recommendations: List[str]
    confidence: float = 0.0  # 0.0 to 1.0
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class AgentQuestion:
    """Decision-support question for an agent."""
    question_id: str
    question_text: str
    question_type: str  # "risk", "timing", "resource", "strategy"
    context: Dict[str, Any]
    priority: int = 3  # 1-5 scale
    suggested_answers: List[str] = None

    def __post_init__(self):
        if self.suggested_answers is None:
            self.suggested_answers = []


@dataclass
class SimulationHealth:
    """Health status of the simulation system."""
    simulation_enabled: bool
    prediction_accuracy: float = 0.0  # 0.0 to 1.0
    average_processing_time_ms: float = 0.0
    total_simulations_run: int = 0
    successful_predictions: int = 0
    failed_predictions: int = 0
    last_health_check: Optional[str] = None
    system_load: float = 0.0  # 0.0 to 1.0

    def __post_init__(self):
        if self.last_health_check is None:
            self.last_health_check = datetime.now().isoformat()


@dataclass
class SimulationConfig:
    """Configuration for the simulation system."""
    enabled: bool = True
    default_look_ahead_minutes: int = 5
    max_look_ahead_minutes: int = 60
    prediction_confidence_threshold: float = 0.3
    risk_score_threshold: float = 0.7
    max_concurrent_simulations: int = 10
    cache_results: bool = True
    cache_ttl_seconds: int = 300


@dataclass
class ForwardSimulationScenario:
    """Complex scenario for forward simulation."""
    scenario_id: str
    name: str
    description: str
    focus_agents: Optional[List[str]] = None
    initial_conditions: Dict[str, Any] = None
    simulation_duration_minutes: int = 30
    expected_outcomes: List[Dict[str, Any]] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.initial_conditions is None:
            self.initial_conditions = {}
        if self.expected_outcomes is None:
            self.expected_outcomes = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
