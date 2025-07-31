# Alinea SDK Backend Integration Guide

## 🎯 Overview

This guide shows how to connect the Alinea SDK to your real Alinea-AI backend system to build production multi-agent systems.

## 🏗️ Current Architecture: Mock vs Real

### Current State (Mock Implementation)
```python
# Current: Simulated coordination
async def intend(self, agent_id, action, affected_resources, context):
    # TODO: Send to coordination service for conflict detection
    # Currently: Just creates intention locally
    intention = Intention(...)
    return intention

async def act(self, intention):
    # TODO: Execute actual action through coordination service  
    # Currently: Simulates success after 0.1s delay
    await asyncio.sleep(0.1)
    return ActionResult(outcome="success")
```

### Target State (Real Backend)
```python
# Real: Connected to Alinea-AI backend
async def intend(self, agent_id, action, affected_resources, context):
    response = await self._post("/coordination/intend", {
        "agent_id": agent_id,
        "action": action, 
        "affected_resources": affected_resources,
        "context": context
    })
    return Intention.from_dict(response.data)

async def act(self, intention):
    response = await self._post("/coordination/act", {
        "intention_id": intention.intention_id
    })
    return ActionResult.from_dict(response.data)
```

## 🔌 Integration Points by Component

### 1. Core Coordination (`coordinator.py`)
**Backend Requirements:**
```
POST /coordination/intend
POST /coordination/act  
GET  /patterns/confidence/{pattern_id}
GET  /adaptation/metrics
GET  /migration/status
```

### 2. Causality Analysis (`causality.py`)  
**Backend Requirements:**
```
POST /causality/trace
POST /causality/impact
POST /causality/counterfactual
GET  /temporal/dependencies/{agent_id}
```

### 3. Memory Management (`memory.py`)
**Backend Requirements:**
```
POST /memory/patterns
GET  /memory/patterns/{pattern_id}
POST /memory/patterns/search
POST /memory/surprises
GET  /memory/stats
```

### 4. World State (`world_state.py`)
**Backend Requirements:**
```
GET  /world/state
POST /world/state/{resource}
POST /world/locks/acquire
DELETE /world/locks/{resource}
POST /agents/register
DELETE /agents/{agent_id}
GET  /world/history/{resource}
```

## 🚀 Step-by-Step Integration

### Step 1: Add HTTP Client
```python
# Add to coordinator.py, causality.py, etc.
import aiohttp
import json

class BaseAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
    
    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.session
    
    async def _post(self, endpoint: str, data: dict):
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        async with session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json()
    
    async def _get(self, endpoint: str):
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
```

### Step 2: Replace Mock Implementations
Replace all TODO sections with real API calls...

## 🔧 Your Backend Needs to Provide

### Core Coordination Service
- **Intention Registration**: Queue and validate agent intentions
- **Resource Conflict Detection**: Check resource availability  
- **Action Execution**: Coordinate actual agent actions
- **Pattern Learning**: Store and retrieve learned patterns

### Temporal Database
- **Event Storage**: Store all agent actions with timestamps
- **Causal Analysis**: Trace event relationships
- **Counterfactual Engine**: Model alternative scenarios

### World State Manager  
- **Distributed State Store**: Consistent state across agents
- **Resource Locking**: Prevent race conditions
- **Agent Registry**: Track active agents
- **HLC Time Synchronization**: Maintain temporal consistency

## 🎯 Building Real Multi-Agent Systems

Once connected, you can build systems like:

### 1. Trading System
```python
# Agent 1: Market Analyzer
intention = await client.intend(
    agent_id="market_analyzer",
    action="analyze_market_trend", 
    affected_resources=["market_data", "trend_models"],
    context={"symbol": "AAPL", "timeframe": "1h"}
)
result = await client.act(intention)

# Agent 2: Risk Manager  
risk_intention = await client.intend(
    agent_id="risk_manager",
    action="assess_portfolio_risk",
    affected_resources=["portfolio_state", "risk_models"], 
    context={"positions": positions}
)
```

### 2. Distributed Computing
```python
# Agent swarm for parallel processing
agents = ["worker_1", "worker_2", "worker_3"]
tasks = []

for i, agent_id in enumerate(agents):
    intention = await client.intend(
        agent_id=agent_id,
        action="process_data_chunk",
        affected_resources=[f"data_chunk_{i}", "temp_storage"],
        context={"chunk_id": i, "algorithm": "map_reduce"}
    )
    tasks.append(client.act(intention))

results = await asyncio.gather(*tasks)
```

## 🔍 Debugging with Causality

When issues occur, trace the problem:
```python
# Something went wrong with agent_42
causal_path = await client.trace_causality("agent_42_failure")

print(f"Failure traced through {len(causal_path.path)} steps:")
for step in causal_path.path:
    print(f"  {step.agent_id} -> {step.action} (impact: {step.causal_strength})")

# Analyze what would happen without the failure
counterfactual = await client.counterfactual_analysis("agent_42_failure")
print(f"Without failure: {counterfactual.outcome_changes}")
```

## 📈 Next Steps

1. **Set up your Alinea-AI backend** with the required endpoints
2. **Replace mock implementations** with real API calls  
3. **Add authentication** and error handling
4. **Build your first multi-agent system**
5. **Use causality tools** for debugging and optimization