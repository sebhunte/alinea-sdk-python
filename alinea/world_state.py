"""
Shared State API for world state management.
"""
import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from .models import WorldSnapshot, APIResponse


class WorldStateManager:
    """
    Shared state management system that provides consistent snapshots
    of the world state across all agents using Hybrid Logical Clocks (HLC).
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self._snapshots: Dict[str, WorldSnapshot] = {}
        self._current_hlc_time = "0"
        self._resource_locks: Dict[str, str] = {}  # resource -> agent_id
        self._active_agents: List[str] = []
    
    async def get_world_state(
        self, 
        resources: List[str], 
        hlc_time: Optional[str] = None
    ) -> WorldSnapshot:
        """
        Get a consistent snapshot of world state for specified resources.
        
        This provides a causally consistent view of the system state
        at a specific Hybrid Logical Clock time.
        
        Args:
            resources: List of resources to include in snapshot (e.g., ["db", "cache"])
            hlc_time: Specific HLC time for the snapshot (e.g., "3150.2")
            
        Returns:
            WorldSnapshot with the requested state
        """
        if hlc_time is None:
            hlc_time = await self._get_current_hlc_time()
        
        snapshot_id = str(uuid.uuid4())
        
        # Get state for each requested resource
        resource_states = {}
        for resource in resources:
            resource_states[resource] = await self._get_resource_state(resource, hlc_time)
        
        # Get current resource locks
        relevant_locks = {
            resource: agent for resource, agent in self._resource_locks.items()
            if resource in resources
        }
        
        snapshot = WorldSnapshot(
            hlc_time=hlc_time,
            resources=resource_states,
            active_agents=self._active_agents.copy(),
            resource_locks=relevant_locks,
            snapshot_id=snapshot_id,
            creation_timestamp=datetime.utcnow().isoformat()
        )
        
        # Cache the snapshot
        self._snapshots[snapshot_id] = snapshot
        
        return snapshot
    
    async def set_resource_state(
        self, 
        resource: str, 
        state: Any, 
        agent_id: str,
        hlc_time: Optional[str] = None
    ) -> bool:
        """
        Set the state of a resource with proper coordination.
        
        Args:
            resource: Resource identifier
            state: New state to set
            agent_id: Agent making the change
            hlc_time: HLC time for the change
            
        Returns:
            True if successful, False if resource is locked by another agent
        """
        if hlc_time is None:
            hlc_time = await self._advance_hlc_time()
        
        # Check if resource is locked by another agent
        if resource in self._resource_locks:
            if self._resource_locks[resource] != agent_id:
                return False  # Resource locked by different agent
        
        # TODO: Update actual resource state in distributed system
        await self._update_resource_state(resource, state, hlc_time)
        
        return True
    
    async def acquire_resource_lock(
        self, 
        resource: str, 
        agent_id: str,
        timeout_seconds: float = 30.0
    ) -> bool:
        """
        Acquire an exclusive lock on a resource.
        
        Args:
            resource: Resource to lock
            agent_id: Agent requesting the lock
            timeout_seconds: Maximum time to wait for the lock
            
        Returns:
            True if lock acquired, False if timeout or already locked
        """
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout_seconds:
            if resource not in self._resource_locks:
                # Resource is available
                self._resource_locks[resource] = agent_id
                # TODO: Persist lock to coordination service
                return True
            
            # Wait a bit before retrying
            await asyncio.sleep(0.1)
        
        return False  # Timeout
    
    async def release_resource_lock(self, resource: str, agent_id: str) -> bool:
        """
        Release a resource lock.
        
        Args:
            resource: Resource to unlock
            agent_id: Agent releasing the lock
            
        Returns:
            True if successfully released, False if not owned by agent
        """
        if resource not in self._resource_locks:
            return True  # Already unlocked
        
        if self._resource_locks[resource] != agent_id:
            return False  # Not owned by this agent
        
        del self._resource_locks[resource]
        # TODO: Remove lock from coordination service
        
        return True
    
    async def register_agent(self, agent_id: str) -> None:
        """
        Register an agent as active in the system.
        
        Args:
            agent_id: Agent to register
        """
        if agent_id not in self._active_agents:
            self._active_agents.append(agent_id)
            # TODO: Register with coordination service
    
    async def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the system.
        
        Args:
            agent_id: Agent to unregister
        """
        if agent_id in self._active_agents:
            self._active_agents.remove(agent_id)
            
        # Release all locks held by this agent
        locks_to_release = [
            resource for resource, holder in self._resource_locks.items()
            if holder == agent_id
        ]
        
        for resource in locks_to_release:
            await self.release_resource_lock(resource, agent_id)
        
        # TODO: Unregister from coordination service
    
    async def get_resource_history(
        self, 
        resource: str,
        start_hlc_time: Optional[str] = None,
        end_hlc_time: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get history of changes to a resource.
        
        Args:
            resource: Resource to get history for
            start_hlc_time: Start of time range
            end_hlc_time: End of time range
            limit: Maximum number of entries to return
            
        Returns:
            List of historical state changes
        """
        # TODO: Implement actual history retrieval from temporal storage
        # For now, return simulated history
        
        return [
            {
                "hlc_time": "3150.1",
                "agent_id": "agent_12",
                "change_type": "update",
                "old_state": {"status": "idle"},
                "new_state": {"status": "processing"},
                "timestamp": "2024-01-15T10:00:00Z"
            },
            {
                "hlc_time": "3150.2",
                "agent_id": "agent_12",
                "change_type": "update", 
                "old_state": {"status": "processing"},
                "new_state": {"status": "completed"},
                "timestamp": "2024-01-15T10:01:30Z"
            }
        ]
    
    async def compare_snapshots(
        self, 
        snapshot1_id: str, 
        snapshot2_id: str
    ) -> Dict[str, Any]:
        """
        Compare two world state snapshots.
        
        Args:
            snapshot1_id: First snapshot to compare
            snapshot2_id: Second snapshot to compare
            
        Returns:
            Dictionary with differences between snapshots
        """
        if (snapshot1_id not in self._snapshots or 
            snapshot2_id not in self._snapshots):
            raise ValueError("One or both snapshots not found")
        
        snap1 = self._snapshots[snapshot1_id]
        snap2 = self._snapshots[snapshot2_id]
        
        differences = {
            "hlc_time_diff": snap2.hlc_time != snap1.hlc_time,
            "resource_changes": {},
            "lock_changes": {},
            "agent_changes": {
                "added": list(set(snap2.active_agents) - set(snap1.active_agents)),
                "removed": list(set(snap1.active_agents) - set(snap2.active_agents))
            }
        }
        
        # Compare resources
        all_resources = set(snap1.resources.keys()).union(set(snap2.resources.keys()))
        for resource in all_resources:
            old_state = snap1.resources.get(resource)
            new_state = snap2.resources.get(resource)
            
            if old_state != new_state:
                differences["resource_changes"][resource] = {
                    "old": old_state,
                    "new": new_state
                }
        
        # Compare locks
        all_lock_resources = set(snap1.resource_locks.keys()).union(set(snap2.resource_locks.keys()))
        for resource in all_lock_resources:
            old_holder = snap1.resource_locks.get(resource)
            new_holder = snap2.resource_locks.get(resource)
            
            if old_holder != new_holder:
                differences["lock_changes"][resource] = {
                    "old_holder": old_holder,
                    "new_holder": new_holder
                }
        
        return differences
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get overall system metrics and health.
        
        Returns:
            Dictionary with system metrics
        """
        return {
            "active_agents": len(self._active_agents),
            "locked_resources": len(self._resource_locks),
            "cached_snapshots": len(self._snapshots),
            "current_hlc_time": self._current_hlc_time,
            "system_health": "healthy",  # Would be computed from real metrics
            "coordination_latency_ms": 15.5,  # Example metric
            "lock_contention_rate": 0.05  # Example metric
        }
    
    async def _get_current_hlc_time(self) -> str:
        """Get current Hybrid Logical Clock time."""
        # TODO: Implement actual HLC synchronization
        # For now, increment a simple counter
        current = float(self._current_hlc_time)
        self._current_hlc_time = str(current + 0.1)
        return self._current_hlc_time
    
    async def _advance_hlc_time(self) -> str:
        """Advance HLC time and return new value."""
        return await self._get_current_hlc_time()
    
    async def _get_resource_state(self, resource: str, hlc_time: str) -> Any:
        """Get the state of a resource at a specific HLC time."""
        # TODO: Query actual distributed state store
        # For now, return simulated state based on resource type
        
        if resource == "db":
            return {
                "connections": 10,
                "active_queries": 3,
                "status": "healthy"
            }
        elif resource == "cache":
            return {
                "memory_usage": "75%",
                "hit_rate": 0.92,
                "entries": 15000
            }
        else:
            return {
                "status": "unknown",
                "last_updated": hlc_time
            }
    
    async def _update_resource_state(self, resource: str, state: Any, hlc_time: str) -> None:
        """Update resource state in the distributed system."""
        # TODO: Implement actual state update to coordination service
        pass