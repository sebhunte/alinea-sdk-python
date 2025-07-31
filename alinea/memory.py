"""
Memory system for pattern history and surprise tracking.
"""
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .models import MemoryPattern, APIResponse


class MemoryManager:
    """
    Memory system that tracks patterns, learns from surprises,
    and maintains historical context for agent coordination.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self._patterns: Dict[str, MemoryPattern] = {}
        self._surprise_threshold = 0.3  # Configurable surprise detection threshold
        self._pattern_decay_hours = 24  # Patterns decay after this time
    
    async def store_pattern(
        self, 
        pattern_id: str,
        pattern_type: str,
        trigger_conditions: Dict[str, Any],
        expected_outcomes: Dict[str, Any],
        confidence: float = 0.5
    ) -> MemoryPattern:
        """
        Store a new learned pattern in memory.
        
        Args:
            pattern_id: Unique identifier for the pattern
            pattern_type: Type of pattern (e.g., "coordination", "resource_usage")
            trigger_conditions: Conditions that trigger this pattern
            expected_outcomes: Expected results when pattern is applied
            confidence: Initial confidence in the pattern
            
        Returns:
            MemoryPattern object that was stored
        """
        pattern = MemoryPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            trigger_conditions=trigger_conditions,
            expected_outcomes=expected_outcomes,
            confidence=confidence,
            usage_count=0,
            last_accessed=datetime.utcnow().isoformat(),
            surprise_events=[]
        )
        
        self._patterns[pattern_id] = pattern
        
        # TODO: Persist to memory storage system
        await self._persist_pattern(pattern)
        
        return pattern
    
    async def get_pattern(self, pattern_id: str) -> Optional[MemoryPattern]:
        """
        Retrieve a pattern from memory.
        
        Args:
            pattern_id: The pattern to retrieve
            
        Returns:
            MemoryPattern if found, None otherwise
        """
        if pattern_id in self._patterns:
            pattern = self._patterns[pattern_id]
            pattern.last_accessed = datetime.utcnow().isoformat()
            pattern.usage_count += 1
            return pattern
        
        # TODO: Try to load from persistent storage
        return await self._load_pattern(pattern_id)
    
    async def find_matching_patterns(
        self, 
        current_context: Dict[str, Any],
        pattern_type: Optional[str] = None
    ) -> List[MemoryPattern]:
        """
        Find patterns that match the current context.
        
        Args:
            current_context: Current situation to match against
            pattern_type: Optional filter by pattern type
            
        Returns:
            List of matching patterns, sorted by relevance
        """
        matching_patterns = []
        
        for pattern in self._patterns.values():
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
                
            relevance_score = await self._calculate_pattern_relevance(
                pattern, current_context
            )
            
            if relevance_score > 0.3:  # Minimum relevance threshold
                pattern.usage_count += 1
                pattern.last_accessed = datetime.utcnow().isoformat()
                matching_patterns.append((pattern, relevance_score))
        
        # Sort by relevance score (descending)
        matching_patterns.sort(key=lambda x: x[1], reverse=True)
        
        return [pattern for pattern, _ in matching_patterns]
    
    async def record_surprise(
        self, 
        pattern_id: str,
        expected_outcome: Dict[str, Any],
        actual_outcome: Dict[str, Any],
        context: Dict[str, Any]
    ) -> None:
        """
        Record a surprise event when outcomes don't match expectations.
        
        Args:
            pattern_id: The pattern that had unexpected results
            expected_outcome: What the pattern predicted
            actual_outcome: What actually happened
            context: Context in which the surprise occurred
        """
        if pattern_id not in self._patterns:
            return
        
        pattern = self._patterns[pattern_id]
        
        surprise_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "expected": expected_outcome,
            "actual": actual_outcome,
            "context": context,
            "surprise_magnitude": await self._calculate_surprise_magnitude(
                expected_outcome, actual_outcome
            )
        }
        
        pattern.surprise_events.append(surprise_event)
        
        # Adjust pattern confidence based on surprise
        surprise_magnitude = surprise_event["surprise_magnitude"]
        if surprise_magnitude > self._surprise_threshold:
            # Significant surprise - reduce confidence
            pattern.confidence = max(0.0, pattern.confidence - surprise_magnitude * 0.5)
        
        # TODO: Trigger pattern relearning if too many surprises
        if len(pattern.surprise_events) > 5:
            await self._trigger_pattern_relearning(pattern_id)
    
    async def get_surprise_history(
        self, 
        pattern_id: Optional[str] = None,
        time_window_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get history of surprise events.
        
        Args:
            pattern_id: Optional filter by specific pattern
            time_window_hours: How far back to look
            
        Returns:
            List of surprise events within the time window
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        cutoff_iso = cutoff_time.isoformat()
        
        surprises = []
        
        patterns_to_check = (
            [self._patterns[pattern_id]] if pattern_id and pattern_id in self._patterns
            else self._patterns.values()
        )
        
        for pattern in patterns_to_check:
            for surprise in pattern.surprise_events:
                if surprise["timestamp"] >= cutoff_iso:
                    surprise_with_pattern = surprise.copy()
                    surprise_with_pattern["pattern_id"] = pattern.pattern_id
                    surprises.append(surprise_with_pattern)
        
        # Sort by timestamp (most recent first)
        surprises.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return surprises
    
    async def cleanup_old_patterns(self) -> int:
        """
        Clean up old, unused patterns to prevent memory bloat.
        
        Returns:
            Number of patterns cleaned up
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=self._pattern_decay_hours)
        cutoff_iso = cutoff_time.isoformat()
        
        patterns_to_remove = []
        
        for pattern_id, pattern in self._patterns.items():
            # Remove if not accessed recently and low confidence
            if (pattern.last_accessed < cutoff_iso and 
                pattern.confidence < 0.3 and 
                pattern.usage_count < 3):
                patterns_to_remove.append(pattern_id)
        
        for pattern_id in patterns_to_remove:
            del self._patterns[pattern_id]
            # TODO: Remove from persistent storage
        
        return len(patterns_to_remove)
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system.
        
        Returns:
            Dictionary with memory statistics
        """
        total_patterns = len(self._patterns)
        high_confidence = sum(1 for p in self._patterns.values() if p.confidence > 0.8)
        total_surprises = sum(len(p.surprise_events) for p in self._patterns.values())
        
        # Calculate average pattern age
        now = datetime.utcnow()
        total_age_hours = 0
        for pattern in self._patterns.values():
            last_accessed = datetime.fromisoformat(pattern.last_accessed.replace('Z', '+00:00'))
            age_hours = (now - last_accessed.replace(tzinfo=None)).total_seconds() / 3600
            total_age_hours += age_hours
        
        avg_age_hours = total_age_hours / total_patterns if total_patterns > 0 else 0
        
        return {
            "total_patterns": total_patterns,
            "high_confidence_patterns": high_confidence,
            "total_surprises": total_surprises,
            "average_pattern_age_hours": round(avg_age_hours, 2),
            "memory_efficiency": round(high_confidence / total_patterns, 2) if total_patterns > 0 else 0
        }
    
    async def _calculate_pattern_relevance(
        self, 
        pattern: MemoryPattern, 
        context: Dict[str, Any]
    ) -> float:
        """Calculate how relevant a pattern is to the current context."""
        # TODO: Implement sophisticated pattern matching
        # For now, simple key-based matching
        
        pattern_keys = set(pattern.trigger_conditions.keys())
        context_keys = set(context.keys())
        
        if not pattern_keys:
            return 0.0
        
        # Calculate overlap
        overlap = len(pattern_keys.intersection(context_keys))
        relevance = overlap / len(pattern_keys)
        
        # Boost relevance based on pattern confidence and usage
        confidence_boost = pattern.confidence * 0.3
        usage_boost = min(pattern.usage_count / 10, 0.2)  # Cap at 0.2
        
        return min(1.0, relevance + confidence_boost + usage_boost)
    
    async def _calculate_surprise_magnitude(
        self, 
        expected: Dict[str, Any], 
        actual: Dict[str, Any]
    ) -> float:
        """Calculate the magnitude of surprise between expected and actual outcomes."""
        # TODO: Implement sophisticated surprise calculation
        # For now, simple difference counting
        
        if not expected and not actual:
            return 0.0
        
        all_keys = set(expected.keys()).union(set(actual.keys()))
        differences = 0
        
        for key in all_keys:
            exp_val = expected.get(key)
            act_val = actual.get(key)
            
            if exp_val != act_val:
                differences += 1
        
        return min(1.0, differences / len(all_keys)) if all_keys else 0.0
    
    async def _persist_pattern(self, pattern: MemoryPattern) -> None:
        """Persist pattern to storage (placeholder)."""
        # TODO: Implement actual persistence
        pass
    
    async def _load_pattern(self, pattern_id: str) -> Optional[MemoryPattern]:
        """Load pattern from storage (placeholder)."""
        # TODO: Implement actual loading
        return None
    
    async def _trigger_pattern_relearning(self, pattern_id: str) -> None:
        """Trigger relearning of a pattern due to too many surprises."""
        # TODO: Implement pattern relearning mechanism
        if pattern_id in self._patterns:
            pattern = self._patterns[pattern_id]
            # Reset confidence and clear old surprises
            pattern.confidence = max(0.1, pattern.confidence * 0.5)
            pattern.surprise_events = pattern.surprise_events[-2:]  # Keep only recent surprises