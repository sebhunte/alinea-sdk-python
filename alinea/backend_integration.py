"""
Backend integration module for connecting SDK to real Alinea-AI services.
"""
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .models import *
from .exceptions import APIError, AuthenticationError, TimeoutError


class AlineaAPIClient:
    """
    HTTP client for communicating with Alinea-AI backend services.
    """
    
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with authentication."""
        if not self.session or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "alinea-sdk-python/0.1.0"
                }
            )
        return self.session
    
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated HTTP request to backend."""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(method, url, json=data) as response:
                if response.status == 401:
                    raise AuthenticationError(
                        "Authentication failed. Check your API key.",
                        status_code=401
                    )
                elif response.status == 403:
                    raise AuthenticationError(
                        "Access forbidden. Insufficient permissions.",
                        status_code=403
                    )
                elif response.status >= 400:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    raise APIError(
                        f"API request failed: {response.status} {response.reason}",
                        status_code=response.status,
                        response=error_data
                    )
                
                return await response.json()
                
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request to {endpoint} timed out after {self.timeout}s")
        except aiohttp.ClientError as e:
            raise APIError(f"Network error: {str(e)}")
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request."""
        return await self._request("POST", endpoint, data)
    
    async def get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request."""
        return await self._request("GET", endpoint)
    
    async def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request."""
        return await self._request("PUT", endpoint, data)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self._request("DELETE", endpoint)


class RealCoordinator:
    """
    Real coordination implementation that connects to Alinea-AI backend.
    """
    
    def __init__(self, api_client: AlineaAPIClient):
        self.api = api_client
        self._active_intentions: Dict[str, Intention] = {}
    
    async def intend(
        self, 
        agent_id: str, 
        action: str, 
        affected_resources: List[str], 
        context: Dict[str, Any]
    ) -> Intention:
        """Register intention with real coordination service."""
        response = await self.api.post("/coordination/intend", {
            "agent_id": agent_id,
            "action": action,
            "affected_resources": affected_resources,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        intention = Intention(
            agent_id=agent_id,
            action=action,
            affected_resources=affected_resources,
            context=context,
            intention_id=response["intention_id"],
            timestamp=response["timestamp"],
            confidence=response.get("confidence", 0.7)
        )
        
        self._active_intentions[intention.intention_id] = intention
        return intention
    
    async def act(self, intention: Intention) -> ActionResult:
        """Execute intention through real coordination service."""
        if intention.intention_id not in self._active_intentions:
            raise ValueError(f"Intention {intention.intention_id} not found")
        
        response = await self.api.post("/coordination/act", {
            "intention_id": intention.intention_id,
            "agent_id": intention.agent_id
        })
        
        result = ActionResult(
            intention_id=intention.intention_id,
            outcome=response["outcome"],
            reason=response.get("reason"),
            debug_info=response.get("debug_info"),
            execution_time=response.get("execution_time"),
            timestamp=response["timestamp"]
        )
        
        # Clean up
        self._active_intentions.pop(intention.intention_id, None)
        return result
    
    async def get_pattern_confidence(self, pattern_id: str) -> float:
        """Get real pattern confidence from learning service."""
        response = await self.api.get(f"/patterns/confidence/{pattern_id}")
        return response["confidence"]
    
    async def get_adaptation_metrics(self) -> AdaptationMetrics:
        """Get real adaptation metrics."""
        response = await self.api.get("/adaptation/metrics")
        return AdaptationMetrics(
            total_patterns=response["total_patterns"],
            high_confidence_patterns=response["high_confidence_patterns"],
            learning_rate=response["learning_rate"],
            surprise_events=response["surprise_events"],
            adaptation_score=response["adaptation_score"],
            last_updated=response["last_updated"]
        )


class RealCausality:
    """Real causality analysis connected to temporal database."""
    
    def __init__(self, api_client: AlineaAPIClient):
        self.api = api_client
    
    async def trace_causality(self, target_event: str) -> CausalPath:
        """Trace real causal relationships from temporal database."""
        response = await self.api.post("/causality/trace", {
            "target_event": target_event,
            "max_depth": 10,
            "min_confidence": 0.1
        })
        
        causal_nodes = [
            CausalNode(
                agent_id=node["agent_id"],
                action=node["action"], 
                timestamp=node["timestamp"],
                resource_changes=node["resource_changes"],
                causal_strength=node["causal_strength"]
            )
            for node in response["causal_path"]
        ]
        
        return CausalPath(
            target_event=target_event,
            path=causal_nodes,
            confidence=response["confidence"],
            total_impact_score=response["total_impact_score"]
        )
    
    async def analyze_impact(self, source_change: str) -> ImpactAnalysis:
        """Analyze real impact through event propagation tracking."""
        response = await self.api.post("/causality/impact", {
            "source_change": source_change,
            "time_window": "24h"
        })
        
        return ImpactAnalysis(
            source_agent=response["source_agent"],
            source_action=response["source_action"],
            affected_agents=response["affected_agents"],
            impact_score=response["impact_score"],
            impact_details=response["impact_details"],
            propagation_time=response["propagation_time"]
        )


class RealWorldState:
    """Real world state management with distributed consistency."""
    
    def __init__(self, api_client: AlineaAPIClient):
        self.api = api_client
    
    async def get_world_state(
        self, 
        resources: List[str], 
        hlc_time: Optional[str] = None
    ) -> WorldSnapshot:
        """Get consistent world state from distributed state store."""
        response = await self.api.post("/world/state", {
            "resources": resources,
            "hlc_time": hlc_time,
            "consistency_level": "strong"
        })
        
        return WorldSnapshot(
            hlc_time=response["hlc_time"],
            resources=response["resources"],
            active_agents=response["active_agents"],
            resource_locks=response["resource_locks"],
            snapshot_id=response["snapshot_id"],
            creation_timestamp=response["creation_timestamp"]
        )
    
    async def acquire_resource_lock(
        self, 
        resource: str, 
        agent_id: str,
        timeout_seconds: float = 30.0
    ) -> bool:
        """Acquire distributed resource lock."""
        try:
            response = await self.api.post("/world/locks/acquire", {
                "resource": resource,
                "agent_id": agent_id,
                "timeout_seconds": timeout_seconds
            })
            return response["acquired"]
        except APIError as e:
            if e.status_code == 409:  # Conflict - already locked
                return False
            raise
    
    async def release_resource_lock(self, resource: str, agent_id: str) -> bool:
        """Release distributed resource lock."""
        try:
            response = await self.api.delete(f"/world/locks/{resource}")
            return response["released"]
        except APIError as e:
            if e.status_code == 404:  # Not found - already unlocked
                return True
            raise


class RealMemory:
    """Real memory management with persistent storage."""
    
    def __init__(self, api_client: AlineaAPIClient):
        self.api = api_client
    
    async def store_pattern(
        self, 
        pattern_id: str,
        pattern_type: str,
        trigger_conditions: Dict[str, Any],
        expected_outcomes: Dict[str, Any],
        confidence: float = 0.5
    ) -> MemoryPattern:
        """Store pattern in persistent memory store."""
        response = await self.api.post("/memory/patterns", {
            "pattern_id": pattern_id,
            "pattern_type": pattern_type,
            "trigger_conditions": trigger_conditions,
            "expected_outcomes": expected_outcomes,
            "confidence": confidence
        })
        
        return MemoryPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            trigger_conditions=trigger_conditions,
            expected_outcomes=expected_outcomes,
            confidence=confidence,
            usage_count=0,
            last_accessed=response["created_at"],
            surprise_events=[]
        )
    
    async def find_matching_patterns(
        self, 
        current_context: Dict[str, Any],
        pattern_type: Optional[str] = None
    ) -> List[MemoryPattern]:
        """Find patterns using real semantic matching."""
        response = await self.api.post("/memory/patterns/search", {
            "context": current_context,
            "pattern_type": pattern_type,
            "min_relevance": 0.3,
            "limit": 10
        })
        
        return [
            MemoryPattern(
                pattern_id=p["pattern_id"],
                pattern_type=p["pattern_type"],
                trigger_conditions=p["trigger_conditions"],
                expected_outcomes=p["expected_outcomes"],
                confidence=p["confidence"],
                usage_count=p["usage_count"],
                last_accessed=p["last_accessed"],
                surprise_events=p["surprise_events"]
            )
            for p in response["patterns"]
        ]