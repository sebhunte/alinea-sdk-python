"""
Test connection to real alinea-ai backend with proper authentication.
"""
import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alinea.real_client import RealAlineaClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_real_backend_connection():
    """Test connection to real alinea-ai backend."""
    logger.info("🔑 Testing Real Backend Authentication")
    
    # Use API key from environment variable
    api_key = os.getenv("ALINEA_API_KEY")
    if not api_key:
        logger.error("❌ ALINEA_API_KEY environment variable not set")
        logger.error("   Set it with: export ALINEA_API_KEY=your_api_key_here")
        return False
    
    client = RealAlineaClient(
        base_url="http://localhost:8000",
        api_key=api_key
    )
    
    try:
        logger.info("📡 Testing memory-first coordination...")
        
        # Test real backend API call
        intention = await client.intend(
            agent_id="auth_test_agent",
            action="test_authentication",
            affected_resources=["auth_test_resource"],
            context={
                "test": True,
                "purpose": "verify_api_key_authentication"
            }
        )
        
        logger.info(f"✅ Intention created: {intention.intention_id}")
        logger.info(f"   Agent: {intention.agent_id}")
        logger.info(f"   Action: {intention.action}")
        logger.info(f"   Confidence: {intention.confidence}")
        
        # Execute the intention
        result = await client.act(intention)
        
        logger.info(f"✅ Action executed: {result.outcome}")
        logger.info(f"   Execution time: {result.execution_time:.2f}s")
        logger.info(f"   Reason: {result.reason}")
        
        logger.info("🎉 AUTHENTICATION SUCCESS!")
        logger.info("   ✅ API key properly authenticated")
        logger.info("   ✅ Bearer token format working")
        logger.info("   ✅ SDK connected to real backend")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Authentication test failed: {e}")
        logger.error("   Check that:")
        logger.error("   1. alinea-ai backend is running on localhost:8000")
        logger.error("   2. API key exists in the users database")
        logger.error("   3. Bearer token authentication is working")
        return False
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_real_backend_connection())