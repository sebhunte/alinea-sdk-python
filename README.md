# 🚀 Alinea SDK for Python

**Memory-First Coordination SDK for Multi-Agent Systems**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Integration Status](https://img.shields.io/badge/Backend%20Integration-✅%20Complete-green.svg)]()

A memory-first coordination SDK for multi-agent systems, providing causality analysis, temporal debugging, and adaptive learning capabilities.

## 🎯 Overview

The Alinea SDK implements a comprehensive coordination framework with four core APIs:

### ✳️ Core Coordination API
Memory-first coordination using the intend/act pattern:

```python
import alinea

client = alinea.AlineaClient()

# Register intention
intention = await client.intend(
    agent_id="agent_1",
    action="process_data",
    affected_resources=["database", "cache"],
    context={"priority": "high"}
)

# Execute intention
result = await client.act(intention)
# result.outcome: "success" | "failure"
```

### 🧠 TD Learning & Adaptation API
Pattern learning and system adaptation:

```python
# Get pattern confidence
confidence = await client.get_pattern_confidence("plan_task_1_resources")

# Get adaptation metrics
metrics = await client.get_adaptation_metrics()

# Check migration status
status = await client.get_migration_status()
```

### 🧬 Causality & Temporal Debugging
Trace causality and analyze counterfactuals:

```python
# Trace causal path to failure
causal_path = await client.trace_causality("agent_42_failure")

# Analyze impact of changes
impact = await client.analyze_impact("agent_12_change")

# Counterfactual analysis
cf = await client.counterfactual_analysis("agent_23_commit", timestamp="3012.5")
```

### 🌍 Shared State API
Consistent world state with Hybrid Logical Clocks:

```python
# Get world state snapshot
snapshot = await client.get_world_state(["db", "cache"], hlc_time="3150.2")
```

## 🚀 Installation

```bash
pip install alinea-sdk
```

For development:
```bash
pip install alinea-sdk[dev]
```

## 📖 Quick Start

```python
import asyncio
import alinea

async def main():
    # Initialize client
    client = alinea.AlineaClient()
    
    # Register your agent
    await client.register_agent("my_agent")
    
    # Coordinate with other agents
    intention = await client.intend(
        agent_id="my_agent",
        action="example_task",
        affected_resources=["shared_resource"],
        context={"type": "demo"}
    )
    
    result = await client.act(intention)
    print(f"Task result: {result.outcome}")
    
    # Get system insights
    snapshot = await client.get_world_state(["shared_resource"])
    health = await client.get_system_health()
    
    print(f"System health: {health['overall_health']}")

asyncio.run(main())
```

## 🧪 Examples

Run the comprehensive demo:

```bash
python examples/multi_agent_demo.py
```

Or use the CLI:
```bash
alinea-demo
```

## 🏗️ Architecture

The SDK is organized into focused modules:

```
alinea/
├── client.py          # Main unified client
├── coordinator.py     # Core coordination & TD learning
├── memory.py          # Pattern history & surprise tracking
├── causality.py       # Causality analysis & debugging
├── world_state.py     # Shared state management
├── models.py          # Data models
└── exceptions.py      # Exception classes
```

## 🔧 Configuration

Configure the client with your coordination service:

```python
client = alinea.AlineaClient(
    base_url="https://your-alinea-service.com",
    api_key="your-api-key"
)
```

## 🧪 Testing

Run tests:
```bash
pytest
```

With coverage:
```bash
pytest --cov=alinea
```

## 📚 Documentation

- [API Reference](https://alinea-sdk-python.readthedocs.io/)
- [User Guide](https://alinea-sdk-python.readthedocs.io/en/latest/guide/)
- [Examples](https://alinea-sdk-python.readthedocs.io/en/latest/examples/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/alinea-ai/alinea-sdk-python
cd alinea-sdk-python
pip install -e .[dev]
pre-commit install
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Homepage](https://alinea.ai)
- [Documentation](https://alinea-sdk-python.readthedocs.io/)
- [GitHub](https://github.com/alinea-ai/alinea-sdk-python)
- [Issues](https://github.com/alinea-ai/alinea-sdk-python/issues)

## 🏷️ Version

Current version: **0.1.0**

This is an alpha release. APIs may change in future versions.