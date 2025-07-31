"""
Example of a real multi-agent system connected to Alinea-AI backend.

This demonstrates how to build production multi-agent systems using
the Alinea SDK connected to your real backend infrastructure.
"""
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

# Import the real backend integration
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alinea import AlineaClient
from alinea.backend_integration import AlineaAPIClient, RealCoordinator, RealCausality, RealWorldState, RealMemory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionAlineaClient(AlineaClient):
    """
    Production version of AlineaClient connected to real Alinea-AI backend.
    """
    
    def __init__(self, base_url: str, api_key: str):
        # Initialize with real backend integration
        self.base_url = base_url
        self.api_key = api_key
        
        # Create API client
        self.api_client = AlineaAPIClient(base_url, api_key)
        
        # Initialize real implementations
        self.coordinator = RealCoordinator(self.api_client)
        self.causality = RealCausality(self.api_client)
        self.world_state = RealWorldState(self.api_client)
        self.memory = RealMemory(self.api_client)
    
    async def close(self):
        """Clean up resources."""
        await self.api_client.close()


class TradingAgent:
    """A trading agent that uses real Alinea coordination."""
    
    def __init__(self, agent_id: str, client: ProductionAlineaClient):
        self.agent_id = agent_id
        self.client = client
        self.positions = {}
        self.last_analysis = None
    
    async def analyze_market(self, symbol: str) -> Dict[str, Any]:
        """Analyze market conditions for a symbol."""
        logger.info(f"[{self.agent_id}] Analyzing market for {symbol}")
        
        # Register intention to analyze market
        intention = await self.client.intend(
            agent_id=self.agent_id,
            action="analyze_market",
            affected_resources=[f"market_data_{symbol}", "analysis_models"],
            context={
                "symbol": symbol,
                "analysis_type": "technical",
                "timeframe": "1h",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Execute the analysis
        result = await self.client.act(intention)
        
        if result.outcome == "success":
            # Store the analysis pattern for learning
            await self.client.store_pattern(
                pattern_id=f"{self.agent_id}_market_analysis",
                pattern_type="market_analysis",
                trigger_conditions={"symbol": symbol, "timeframe": "1h"},
                expected_outcomes={"analysis_quality": "high", "prediction_accuracy": 0.75},
                confidence=0.8
            )
            
            self.last_analysis = {
                "symbol": symbol,
                "trend": "bullish",  # Would come from real analysis
                "confidence": 0.78,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"[{self.agent_id}] Market analysis completed for {symbol}")
            return self.last_analysis
        else:
            logger.error(f"[{self.agent_id}] Market analysis failed: {result.reason}")
            return {}


class RiskAgent:
    """Risk management agent for portfolio oversight."""
    
    def __init__(self, agent_id: str, client: ProductionAlineaClient):
        self.agent_id = agent_id
        self.client = client
        self.risk_limits = {"max_position_size": 10000, "max_portfolio_risk": 0.02}
    
    async def assess_portfolio_risk(self, positions: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall portfolio risk."""
        logger.info(f"[{self.agent_id}] Assessing portfolio risk")
        
        # Check if we need to acquire exclusive access to risk models
        lock_acquired = await self.client.acquire_resource_lock(
            "risk_models", self.agent_id, timeout_seconds=10.0
        )
        
        if not lock_acquired:
            logger.warning(f"[{self.agent_id}] Could not acquire risk model lock")
            return {"status": "retry_later"}
        
        try:
            intention = await self.client.intend(
                agent_id=self.agent_id,
                action="assess_portfolio_risk",
                affected_resources=["portfolio_state", "risk_models"],
                context={
                    "positions": positions,
                    "risk_limits": self.risk_limits,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            result = await self.client.act(intention)
            
            if result.outcome == "success":
                risk_assessment = {
                    "portfolio_var": 0.015,  # Would come from real calculation
                    "position_risks": {"AAPL": 0.003, "GOOGL": 0.005},
                    "recommendations": ["reduce_position_GOOGL"],
                    "overall_risk": "moderate"
                }
                
                logger.info(f"[{self.agent_id}] Risk assessment completed")
                return risk_assessment
            else:
                logger.error(f"[{self.agent_id}] Risk assessment failed: {result.reason}")
                return {"status": "error", "message": result.reason}
                
        finally:
            # Always release the lock
            await self.client.release_resource_lock("risk_models", self.agent_id)


class ExecutionAgent:
    """Trade execution agent."""
    
    def __init__(self, agent_id: str, client: ProductionAlineaClient):
        self.agent_id = agent_id
        self.client = client
    
    async def execute_trade(
        self, 
        symbol: str, 
        action: str, 
        quantity: int,
        analysis: Dict[str, Any],
        risk_approval: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a trade with proper coordination."""
        logger.info(f"[{self.agent_id}] Executing {action} {quantity} {symbol}")
        
        # Register intention to execute trade
        intention = await self.client.intend(
            agent_id=self.agent_id,
            action="execute_trade",
            affected_resources=[f"portfolio_state", f"market_access_{symbol}"],
            context={
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "analysis": analysis,
                "risk_approval": risk_approval,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        result = await self.client.act(intention)
        
        if result.outcome == "success":
            execution_result = {
                "trade_id": f"trade_{datetime.utcnow().timestamp()}",
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "price": 150.25,  # Would come from real execution
                "status": "filled",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"[{self.agent_id}] Trade executed successfully: {execution_result['trade_id']}")
            return execution_result
        else:
            logger.error(f"[{self.agent_id}] Trade execution failed: {result.reason}")
            
            # Record surprise if execution was expected to succeed
            if risk_approval.get("approved", False):
                await self.client.record_surprise(
                    pattern_id=f"{self.agent_id}_execution_pattern",
                    expected_outcome={"status": "filled"},
                    actual_outcome={"status": "failed", "reason": result.reason},
                    context={"symbol": symbol, "market_conditions": "normal"}
                )
            
            return {"status": "failed", "reason": result.reason}


async def demonstrate_production_trading_system():
    """Demonstrate a production multi-agent trading system."""
    logger.info("=== Production Multi-Agent Trading System ===")
    
    # Connect to real Alinea-AI backend
    client = ProductionAlineaClient(
        base_url="https://api.alinea.ai",  # Your real backend URL
        api_key="your-production-api-key"   # Your real API key
    )
    
    try:
        # Create specialized agents
        market_agent = TradingAgent("market_analyzer", client)
        risk_agent = RiskAgent("risk_manager", client)
        execution_agent = ExecutionAgent("trade_executor", client)
        
        # Register all agents with the system
        await client.register_agent("market_analyzer")
        await client.register_agent("risk_manager")
        await client.register_agent("trade_executor")
        
        # Orchestrated trading workflow
        symbol = "AAPL"
        
        # Step 1: Market Analysis
        analysis = await market_agent.analyze_market(symbol)
        
        if analysis.get("trend") == "bullish":
            logger.info("Market analysis suggests bullish trend")
            
            # Step 2: Risk Assessment
            current_positions = {"AAPL": 500, "GOOGL": 300}  # Current portfolio
            risk_assessment = await risk_agent.assess_portfolio_risk(current_positions)
            
            if risk_assessment.get("overall_risk") in ["low", "moderate"]:
                logger.info("Risk assessment approved for trading")
                
                # Step 3: Execute Trade
                trade_result = await execution_agent.execute_trade(
                    symbol=symbol,
                    action="buy",
                    quantity=100,
                    analysis=analysis,
                    risk_approval={"approved": True, "risk_level": risk_assessment["overall_risk"]}
                )
                
                if trade_result.get("status") == "filled":
                    logger.info(f"Trade completed successfully: {trade_result['trade_id']}")
                else:
                    logger.error("Trade execution failed")
            else:
                logger.warning("Risk assessment rejected the trade")
        else:
            logger.info("Market conditions not favorable for trading")
        
        # Demonstrate causality analysis for debugging
        await demonstrate_causality_debugging(client)
        
    except Exception as e:
        logger.error(f"Trading system error: {e}")
        
        # Use causality analysis to understand what went wrong
        causal_path = await client.trace_causality("trading_system_error")
        logger.info(f"Error traced through {len(causal_path.path)} steps")
        
    finally:
        # Clean up
        await client.unregister_agent("market_analyzer")
        await client.unregister_agent("risk_manager") 
        await client.unregister_agent("trade_executor")
        await client.close()


async def demonstrate_causality_debugging(client: ProductionAlineaClient):
    """Show how to use causality analysis for system debugging."""
    logger.info("=== Causality Analysis Demonstration ===")
    
    # Analyze the impact of the market analysis on the system
    impact = await client.analyze_impact("market_analyzer_analysis")
    logger.info(f"Market analysis impacted {len(impact.affected_agents)} agents")
    logger.info(f"Impact details: {impact.impact_details}")
    
    # What-if analysis: What if the market analysis had failed?
    counterfactual = await client.counterfactual_analysis(
        "market_analyzer_analysis", 
        timestamp=datetime.utcnow().isoformat()
    )
    logger.info(f"Counterfactual analysis:")
    logger.info(f"  Probability difference: {counterfactual.probability_difference}")
    logger.info(f"  Outcome changes: {counterfactual.outcome_changes}")


async def main():
    """Run the production multi-agent system demonstration."""
    logger.info("Starting Production Multi-Agent System Demo")
    logger.info("=" * 60)
    
    try:
        await demonstrate_production_trading_system()
        
        logger.info("=" * 60)
        logger.info("Production demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    # Run the production demo
    asyncio.run(main())