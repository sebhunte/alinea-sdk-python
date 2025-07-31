"""
Quick start example connecting to real alinea-ai backend.
"""
import asyncio
import logging
import os
from alinea.real_client import RealAlineaClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Connect to real backend with your API key
    client = RealAlineaClient(
        base_url="http://localhost:8000",
        api_key=os.getenv("ALINEA_API_KEY", "your-api-key-here")  # Set via environment variable
    )
    
    try:
        logger.info("🚀 Quick Start: SDK → Real Backend")
        
        # Memory-first coordination
        intention = await client.intend(
            agent_id="quickstart_agent",
            action="demo_task",
            affected_resources=["demo_resource"],
            context={"demo": True}
        )
        
        result = await client.act(intention)
        logger.info(f"✅ Task completed: {result.outcome}")
        
        # Causality analysis
        causal_path = await client.trace_causality("quickstart_agent")
        logger.info(f"🔍 Found {len(causal_path.path)} causal steps")
        
        logger.info("SDK successfully connected to real alinea-ai backend!")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
