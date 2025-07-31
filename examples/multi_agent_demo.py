"""
Comprehensive multi-agent demo showcasing all Alinea SDK APIs.

This demo demonstrates:
- Core coordination with intend/act pattern
- Pattern learning and adaptation
- Causality analysis and debugging
- Shared world state management
- Memory pattern tracking
"""
import asyncio
import logging
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alinea import AlineaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoAgent:
    """A demo agent that uses the Alinea SDK for coordination."""
    
    def __init__(self, agent_id: str, client: AlineaClient):
        self.agent_id = agent_id
        self.client = client
        self.completed_tasks = 0
    
    async def process_task(self, task_id: str, resources: list, context: Dict[str, Any]):
        """Process a task using the full coordination pattern."""
        logger.info(f"[{self.agent_id}] Starting task {task_id}")
        
        # Step 1: Register intention
        intention = await self.client.intend(
            agent_id=self.agent_id,
            action=f"process_task_{task_id}",
            affected_resources=resources,
            context=context
        )
        logger.info(f"[{self.agent_id}] Registered intention {intention.intention_id}")
        
        # Step 2: Acquire resource locks if needed
        locks_acquired = []
        for resource in resources:
            if await self.client.acquire_resource_lock(resource, self.agent_id, timeout_seconds=5.0):
                locks_acquired.append(resource)
                logger.info(f"[{self.agent_id}] Acquired lock on {resource}")
            else:
                logger.warning(f"[{self.agent_id}] Failed to acquire lock on {resource}")
        
        try:
            # Step 3: Execute the intention
            result = await self.client.act(intention)
            
            if result.outcome == "success":
                logger.info(f"[{self.agent_id}] Task {task_id} completed successfully")
                self.completed_tasks += 1
                
                # Store successful pattern
                await self.client.store_pattern(
                    pattern_id=f"{self.agent_id}_task_pattern",
                    pattern_type="task_execution",
                    trigger_conditions={"resources": resources, "context": context},
                    expected_outcomes={"result": "success", "time": result.execution_time},
                    confidence=0.8
                )
            else:
                logger.error(f"[{self.agent_id}] Task {task_id} failed: {result.reason}")
                
                # Record surprise if this was unexpected
                if context.get("expected_outcome") == "success":
                    await self.client.record_surprise(
                        pattern_id=f"{self.agent_id}_task_pattern",
                        expected_outcome={"result": "success"},
                        actual_outcome={"result": "failure", "reason": result.reason},
                        context=context
                    )
            
            return result
            
        finally:
            # Step 4: Release all acquired locks
            for resource in locks_acquired:
                await self.client.release_resource_lock(resource, self.agent_id)
                logger.info(f"[{self.agent_id}] Released lock on {resource}")


async def demonstrate_core_coordination():
    """Demonstrate the core intend/act coordination pattern."""
    logger.info("=== Demonstrating Core Coordination ===")
    
    client = AlineaClient()
    
    # Create demo agents
    agent1 = DemoAgent("agent_1", client)
    agent2 = DemoAgent("agent_2", client)
    
    # Register agents
    await client.register_agent("agent_1")
    await client.register_agent("agent_2")
    
    # Run concurrent tasks
    tasks = [
        agent1.process_task("task_A", ["database"], {"priority": "high", "expected_outcome": "success"}),
        agent2.process_task("task_B", ["cache"], {"priority": "medium", "expected_outcome": "success"}),
        agent1.process_task("task_C", ["database", "cache"], {"priority": "low", "expected_outcome": "success"})
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Task {i+1} failed with exception: {result}")
        else:
            logger.info(f"Task {i+1} result: {result.outcome}")
    
    # Cleanup
    await client.unregister_agent("agent_1")
    await client.unregister_agent("agent_2")


async def demonstrate_adaptation_learning():
    """Demonstrate TD learning and adaptation features."""
    logger.info("=== Demonstrating Adaptation & Learning ===")
    
    client = AlineaClient()
    
    # Get pattern confidence
    confidence = await client.get_pattern_confidence("agent_1_task_pattern")
    logger.info(f"Pattern confidence: {confidence}")
    
    # Get adaptation metrics
    metrics = await client.get_adaptation_metrics()
    logger.info(f"Adaptation metrics: {metrics}")
    
    # Get migration status
    status = await client.get_migration_status()
    logger.info(f"Migration status: {status.status}")
    
    # Find matching patterns
    current_context = {"priority": "high", "resources": ["database"]}
    patterns = await client.find_matching_patterns(current_context, "task_execution")
    logger.info(f"Found {len(patterns)} matching patterns")


async def demonstrate_causality_analysis():
    """Demonstrate causality and temporal debugging."""
    logger.info("=== Demonstrating Causality Analysis ===")
    
    client = AlineaClient()
    
    # Trace causality of a failure
    causal_path = await client.trace_causality("agent_42_failure")
    logger.info(f"Causal path has {len(causal_path.path)} nodes with confidence {causal_path.confidence}")
    
    for i, node in enumerate(causal_path.path):
        logger.info(f"  Step {i+1}: {node.agent_id} -> {node.action} (strength: {node.causal_strength})")
    
    # Analyze impact of a change
    impact = await client.analyze_impact("agent_12_change")
    logger.info(f"Impact analysis: {impact.affected_agents} agents affected with score {impact.impact_score}")
    
    # Counterfactual analysis
    counterfactual = await client.counterfactual_analysis("agent_23_commit", timestamp="3012.5")
    logger.info(f"Counterfactual: {counterfactual.probability_difference} probability difference")
    logger.info(f"Outcome changes: {counterfactual.outcome_changes}")


async def demonstrate_world_state():
    """Demonstrate shared world state management."""
    logger.info("=== Demonstrating World State Management ===")
    
    client = AlineaClient()
    
    # Get world state snapshot
    snapshot = await client.get_world_state(["database", "cache"], hlc_time="3150.2")
    logger.info(f"World state snapshot {snapshot.snapshot_id} at HLC time {snapshot.hlc_time}")
    logger.info(f"Active agents: {snapshot.active_agents}")
    logger.info(f"Resource locks: {snapshot.resource_locks}")
    logger.info(f"Resources: {list(snapshot.resources.keys())}")
    
    # Get another snapshot to compare
    snapshot2 = await client.get_world_state(["database", "cache"])
    logger.info(f"Second snapshot {snapshot2.snapshot_id} at HLC time {snapshot2.hlc_time}")
    
    # Compare snapshots
    if hasattr(client.world_state, 'compare_snapshots'):
        diff = await client.world_state.compare_snapshots(snapshot.snapshot_id, snapshot2.snapshot_id)
        logger.info(f"Snapshot differences: {diff}")


async def demonstrate_system_health():
    """Demonstrate system health monitoring."""
    logger.info("=== Demonstrating System Health ===")
    
    client = AlineaClient()
    
    # Get comprehensive health metrics
    health = await client.get_system_health()
    logger.info("System Health Report:")
    logger.info(f"  Adaptation: {health['adaptation']['total_patterns']} patterns, {health['adaptation']['adaptation_score']} score")
    logger.info(f"  World State: {health['world_state']['active_agents']} agents, {health['world_state']['locked_resources']} locks")
    logger.info(f"  Memory: {health['memory']['total_patterns']} patterns, {health['memory']['memory_efficiency']} efficiency")
    logger.info(f"  Overall: {health['overall_health']}")


async def main():
    """Run the complete multi-agent demo."""
    logger.info("Starting Alinea SDK Multi-Agent Demo")
    logger.info("=" * 50)
    
    try:
        # Run all demonstrations
        await demonstrate_core_coordination()
        await asyncio.sleep(1)  # Brief pause between demos
        
        await demonstrate_adaptation_learning()
        await asyncio.sleep(1)
        
        await demonstrate_causality_analysis()
        await asyncio.sleep(1)
        
        await demonstrate_world_state()
        await asyncio.sleep(1)
        
        await demonstrate_system_health()
        
        logger.info("=" * 50)
        logger.info("Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
