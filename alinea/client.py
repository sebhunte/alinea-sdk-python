"""
Alinea SDK Client - Unified API access point.
"""
from typing import Dict, List, Any, Optional

from .coordinator import Coordinator
from .memory import MemoryManager
from .causality import CausalityAnalyzer
from .world_state import WorldStateManager
from .models import (
    Intention, ActionResult, PatternConfidence, AdaptationMetrics,
    MigrationStatus, CausalPath, ImpactAnalysis, CounterfactualAnalysis,
    WorldSnapshot, MemoryPattern
)


class AlineaClient:
    """
    Main client for the Alinea SDK providing unified access to all APIs.
    
    This client implements the complete Alinea coordination interface:
    - Core Coordination API (intend/act pattern)
    - TD Learning & Adaptation API  
    - Causality & Temporal Debugging
    - Shared State API
    - Memory management
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize the Alinea client.
        
        Args:
            base_url: Base URL for the Alinea coordination service
            api_key: Optional API key for authentication
        """
        self.base_url = base_url
        self.api_key = api_key
        
        # Initialize all subsystems
        self.coordinator = Coordinator(base_url, api_key)
        self.memory = MemoryManager(base_url, api_key)
        self.causality = CausalityAnalyzer(base_url, api_key)
        self.world_state = WorldStateManager(base_url, api_key)
    
    # Core Coordination API
    async def intend(
        self, 
        agent_id: str, 
        action: str, 
        affected_resources: List[str], 
        context: Dict[str, Any]
    ) -> Intention:
        """Register an intention for an agent to perform an action."""
        return await self.coordinator.intend(agent_id, action, affected_resources, context)
    
    async def act(self, intention: Intention) -> ActionResult:
        """Execute a previously registered intention."""
        return await self.coordinator.act(intention)
    
    # TD Learning & Adaptation API
    async def get_pattern_confidence(self, pattern_id: str) -> float:
        """Get confidence score for a learned pattern."""
        return await self.coordinator.get_pattern_confidence(pattern_id)
    
    async def get_adaptation_metrics(self) -> AdaptationMetrics:
        """Get current system adaptation and learning metrics."""
        return await self.coordinator.get_adaptation_metrics()
    
    async def get_migration_status(self) -> MigrationStatus:
        """Get status of pattern migration and system updates."""
        return await self.coordinator.get_migration_status()
    
    # Causality & Temporal Debugging API
    async def trace_causality(self, target_event: str) -> CausalPath:
        """Trace the causal path leading to a specific event or failure."""
        return await self.causality.trace_causality(target_event)
    
    async def analyze_impact(self, source_change: str) -> ImpactAnalysis:
        """Analyze the impact of an agent's change on the system."""
        return await self.causality.analyze_impact(source_change)
    
    async def counterfactual_analysis(
        self, 
        original_event: str, 
        timestamp: Optional[str] = None
    ) -> CounterfactualAnalysis:
        """Perform counterfactual what-if analysis for alternative timelines."""
        return await self.causality.counterfactual_analysis(original_event, timestamp)
    
    # Shared State API
    async def get_world_state(
        self, 
        resources: List[str], 
        hlc_time: Optional[str] = None
    ) -> WorldSnapshot:
        """Get a consistent snapshot of world state for specified resources."""
        return await self.world_state.get_world_state(resources, hlc_time)
    
    # Extended APIs
    async def register_agent(self, agent_id: str) -> None:
        """Register an agent as active in the system."""
        await self.world_state.register_agent(agent_id)
    
    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the system."""
        await self.world_state.unregister_agent(agent_id)
    
    async def acquire_resource_lock(
        self, 
        resource: str, 
        agent_id: str,
        timeout_seconds: float = 30.0
    ) -> bool:
        """Acquire an exclusive lock on a resource."""
        return await self.world_state.acquire_resource_lock(resource, agent_id, timeout_seconds)
    
    async def release_resource_lock(self, resource: str, agent_id: str) -> bool:
        """Release a resource lock."""
        return await self.world_state.release_resource_lock(resource, agent_id)
    
    async def store_pattern(
        self, 
        pattern_id: str,
        pattern_type: str,
        trigger_conditions: Dict[str, Any],
        expected_outcomes: Dict[str, Any],
        confidence: float = 0.5
    ) -> MemoryPattern:
        """Store a new learned pattern in memory."""
        return await self.memory.store_pattern(
            pattern_id, pattern_type, trigger_conditions, expected_outcomes, confidence
        )
    
    async def find_matching_patterns(
        self, 
        current_context: Dict[str, Any],
        pattern_type: Optional[str] = None
    ) -> List[MemoryPattern]:
        """Find patterns that match the current context."""
        return await self.memory.find_matching_patterns(current_context, pattern_type)
    
    async def record_surprise(
        self, 
        pattern_id: str,
        expected_outcome: Dict[str, Any],
        actual_outcome: Dict[str, Any],
        context: Dict[str, Any]
    ) -> None:
        """Record a surprise event when outcomes don't match expectations."""
        await self.memory.record_surprise(pattern_id, expected_outcome, actual_outcome, context)
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health and metrics."""
        adaptation_metrics = await self.get_adaptation_metrics()
        world_metrics = await self.world_state.get_system_metrics()
        memory_stats = await self.memory.get_memory_stats()
        
        return {
            "adaptation": adaptation_metrics.__dict__,
            "world_state": world_metrics,
            "memory": memory_stats,
            "overall_health": "healthy"
        }