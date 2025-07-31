"""
Alinea SDK - Memory-first coordination for multi-agent systems.
"""

# Core models (import first to avoid circular dependencies)
from .models import (
    Intention,
    ActionResult, 
    PatternConfidence,
    AdaptationMetrics,
    MigrationStatus,
    CausalNode,
    CausalPath,
    ImpactAnalysis,
    CounterfactualAnalysis,
    WorldSnapshot,
    MemoryPattern,
    APIResponse,
    # Forward Simulation Models
    SimulationResult,
    WhatIfAnalysis,
    AgentQuestion,
    SimulationHealth,
    SimulationConfig,
    ForwardSimulationScenario
)

# Individual subsystems
from .coordinator import Coordinator
from .memory import MemoryManager
from .causality import CausalityAnalyzer
from .world_state import WorldStateManager

# Main client
from .client import AlineaClient

# Exceptions
from .exceptions import *

# Version info
__version__ = "0.1.0"
__author__ = "Alinea Team"
__description__ = "Memory-first coordination SDK for multi-agent systems"

# Convenience aliases
Client = AlineaClient

# Main exports
__all__ = [
    # Main client
    "AlineaClient",
    "Client",
    
    # Core models
    "Intention",
    "ActionResult",
    "PatternConfidence", 
    "AdaptationMetrics",
    "MigrationStatus",
    "CausalNode",
    "CausalPath",
    "ImpactAnalysis",
    "CounterfactualAnalysis",
    "WorldSnapshot",
    "MemoryPattern",
    "APIResponse",
    
    # Forward Simulation Models
    "SimulationResult",
    "WhatIfAnalysis",
    "AgentQuestion",
    "SimulationHealth",
    "SimulationConfig",
    "ForwardSimulationScenario",
    
    # Subsystems
    "Coordinator",
    "MemoryManager", 
    "CausalityAnalyzer",
    "WorldStateManager",
    
    # Metadata
    "__version__",
    "__author__",
    "__description__"
]