#!/usr/bin/env python3
"""
🧠 LLM-Based Research & Writing Assistant Workflow

A comprehensive multi-agent system demonstrating intelligent coordination
between LLM agents using Alinea's memory-first architecture.

🤖 Agents:
- Research Agent: Gathers and structures information
- Analysis Agent: Processes and synthesizes data
- Writing Agent: Creates structured content
- Review Agent: Quality assurance and improvement

🎯 Workflow:
Research → Analysis → Writing → Review → Final Output

This example shows:
✅ Memory-first coordination between LLM agents
✅ Real-time causality tracing for debugging
✅ Adaptive learning from agent interactions
✅ Secure API key management
✅ Error handling and recovery patterns
"""

import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import Alinea SDK
from alinea.real_client import RealAlineaClient
from alinea.models import Intention, ActionResult, CausalPath, ImpactAnalysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ResearchTask:
    """Represents a research task flowing through the agent pipeline."""
    topic: str
    requirements: Dict[str, Any]
    research_data: Optional[Dict] = None
    analysis_results: Optional[Dict] = None
    content_draft: Optional[str] = None
    final_output: Optional[str] = None
    quality_score: Optional[float] = None

class LLMAgent:
    """Base class for LLM-powered agents with Alinea coordination."""
    
    def __init__(self, agent_id: str, alinea_client: RealAlineaClient):
        self.agent_id = agent_id
        self.alinea = alinea_client
        self.memory_patterns: Dict[str, Any] = {}
        
    async def register(self):
        """Register agent with Alinea coordination system."""
        try:
            await self.alinea.register_agent(self.agent_id)
            logger.info(f"✅ {self.agent_id} registered successfully")
        except Exception as e:
            logger.error(f"❌ Failed to register {self.agent_id}: {e}")
            
    async def coordinate_action(self, action: str, resources: List[str], context: Dict[str, Any]) -> ActionResult:
        """Coordinate action with other agents using Alinea's intend/act pattern."""
        try:
            # Step 1: Declare intention
            intention = await self.alinea.intend(
                agent_id=self.agent_id,
                action=action,
                affected_resources=resources,
                context=context
            )
            
            logger.info(f"🎯 {self.agent_id} intends: {action}")
            
            # Step 2: Execute coordinated action
            result = await self.alinea.act(intention)
            
            if result.outcome == "success":
                logger.info(f"✅ {self.agent_id} completed: {action}")
            else:
                logger.warning(f"⚠️ {self.agent_id} failed: {action} - {result.debug_info}")
                
            return result
            
        except Exception as e:
            logger.error(f"❌ {self.agent_id} coordination failed: {e}")
            raise

    def simulate_llm_call(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Simulate LLM API call (replace with actual OpenAI/Anthropic/etc. call).
        
        In production, this would be:
        - OpenAI: openai.ChatCompletion.create()
        - Anthropic: anthropic.completions.create()
        - Local model: transformers.pipeline()
        """
        # Simulated response based on agent type and context
        base_responses = {
            "research_agent": f"Researched information about: {context.get('topic', 'unknown topic')}",
            "analysis_agent": f"Analyzed data with insights: {context.get('data_summary', 'no data')}",
            "writing_agent": f"Generated content for: {context.get('content_type', 'general content')}",
            "review_agent": f"Reviewed content with score: {context.get('review_criteria', 'general review')}"
        }
        
        return base_responses.get(self.agent_id, f"LLM response for: {prompt[:50]}...")

class ResearchAgent(LLMAgent):
    """Gathers and structures information from various sources."""
    
    async def research_topic(self, task: ResearchTask) -> ResearchTask:
        """Conduct research on the given topic."""
        
        # Coordinate with Alinea
        result = await self.coordinate_action(
            action="research_topic",
            resources=["web_search", "knowledge_base", "research_cache"],
            context={
                "topic": task.topic,
                "requirements": task.requirements,
                "research_depth": task.requirements.get("depth", "standard")
            }
        )
        
        if result.outcome == "success":
            # Simulate research with LLM
            research_prompt = f"""
            Research the topic: {task.topic}
            Requirements: {task.requirements}
            
            Provide structured research data including:
            - Key facts and statistics
            - Recent developments
            - Expert opinions
            - Relevant sources
            """
            
            # Simulate LLM research call
            llm_response = self.simulate_llm_call(research_prompt, {
                "topic": task.topic,
                "agent_type": "research"
            })
            
            # Structure research data
            task.research_data = {
                "topic": task.topic,
                "key_facts": [
                    "Recent developments in the field",
                    "Statistical insights and trends",
                    "Expert perspectives and opinions"
                ],
                "sources": [
                    "Academic papers",
                    "Industry reports", 
                    "Expert interviews"
                ],
                "llm_insights": llm_response,
                "research_timestamp": datetime.now().isoformat(),
                "confidence_score": 0.85
            }
            
            # Store research pattern in memory
            await self.alinea.store_pattern(
                pattern_id=f"research_{task.topic.replace(' ', '_')}",
                pattern_type="research_success",
                trigger_conditions={"topic_complexity": "medium"},
                expected_outcomes={"data_quality": "high"},
                confidence=0.85
            )
            
            logger.info(f"🔍 Research completed for: {task.topic}")
            
        return task

class AnalysisAgent(LLMAgent):
    """Processes and synthesizes research data."""
    
    async def analyze_research(self, task: ResearchTask) -> ResearchTask:
        """Analyze research data and extract insights."""
        
        if not task.research_data:
            raise ValueError("No research data available for analysis")
            
        # Coordinate with Alinea
        result = await self.coordinate_action(
            action="analyze_research",
            resources=["analysis_engine", "knowledge_graph", "research_cache"],
            context={
                "data_size": len(str(task.research_data)),
                "analysis_type": task.requirements.get("analysis_type", "comprehensive"),
                "research_quality": task.research_data.get("confidence_score", 0.5)
            }
        )
        
        if result.outcome == "success":
            # Simulate analysis with LLM
            analysis_prompt = f"""
            Analyze the following research data:
            {json.dumps(task.research_data, indent=2)}
            
            Provide:
            - Key insights and patterns
            - Synthesis of main themes
            - Contradictions or gaps
            - Actionable conclusions
            """
            
            llm_response = self.simulate_llm_call(analysis_prompt, {
                "data_summary": "research data analysis",
                "agent_type": "analysis"
            })
            
            # Structure analysis results
            task.analysis_results = {
                "key_insights": [
                    "Pattern identification in research data",
                    "Synthesis of multiple perspectives",
                    "Gap analysis and recommendations"
                ],
                "main_themes": [
                    "Primary theme from research",
                    "Secondary supporting themes",
                    "Emerging trends identified"
                ],
                "conclusions": [
                    "Data-driven conclusion 1",
                    "Evidence-based insight 2",
                    "Strategic recommendation 3"
                ],
                "llm_analysis": llm_response,
                "analysis_timestamp": datetime.now().isoformat(),
                "confidence_score": 0.90
            }
            
            logger.info(f"📊 Analysis completed for: {task.topic}")
            
        return task

class WritingAgent(LLMAgent):
    """Creates structured content based on analysis."""
    
    async def generate_content(self, task: ResearchTask) -> ResearchTask:
        """Generate structured content from analysis."""
        
        if not task.analysis_results:
            raise ValueError("No analysis results available for writing")
            
        # Coordinate with Alinea
        result = await self.coordinate_action(
            action="generate_content",
            resources=["content_generator", "style_guide", "template_library"],
            context={
                "content_type": task.requirements.get("output_format", "article"),
                "target_length": task.requirements.get("length", "medium"),
                "tone": task.requirements.get("tone", "professional")
            }
        )
        
        if result.outcome == "success":
            # Simulate content generation with LLM
            writing_prompt = f"""
            Create structured content based on this analysis:
            {json.dumps(task.analysis_results, indent=2)}
            
            Requirements:
            - Format: {task.requirements.get('output_format', 'article')}
            - Length: {task.requirements.get('length', 'medium')}
            - Tone: {task.requirements.get('tone', 'professional')}
            
            Include:
            - Compelling introduction
            - Well-structured main content
            - Evidence-based conclusions
            """
            
            llm_response = self.simulate_llm_call(writing_prompt, {
                "content_type": task.requirements.get("output_format", "article"),
                "agent_type": "writing"
            })
            
            # Generate structured content
            task.content_draft = f"""
# {task.topic}

## Introduction
{task.analysis_results['key_insights'][0]}

## Main Analysis
{chr(10).join(['- ' + theme for theme in task.analysis_results['main_themes']])}

## Key Insights
{chr(10).join(['- ' + insight for insight in task.analysis_results['key_insights']])}

## Conclusions
{chr(10).join(['- ' + conclusion for conclusion in task.analysis_results['conclusions']])}

## LLM Generated Content
{llm_response}

---
*Generated by Alinea LLM Research Workflow*
*Timestamp: {datetime.now().isoformat()}*
            """
            
            logger.info(f"✍️ Content generated for: {task.topic}")
            
        return task

class ReviewAgent(LLMAgent):
    """Quality assurance and content improvement."""
    
    async def review_content(self, task: ResearchTask) -> ResearchTask:
        """Review and improve content quality."""
        
        if not task.content_draft:
            raise ValueError("No content draft available for review")
            
        # Coordinate with Alinea
        result = await self.coordinate_action(
            action="review_content",
            resources=["quality_checker", "grammar_engine", "fact_checker"],
            context={
                "content_length": len(task.content_draft),
                "review_criteria": task.requirements.get("quality_standards", "high"),
                "fact_check_required": True
            }
        )
        
        if result.outcome == "success":
            # Simulate content review with LLM
            review_prompt = f"""
            Review this content for quality, accuracy, and clarity:
            
            {task.content_draft}
            
            Evaluate:
            - Factual accuracy
            - Logical flow
            - Writing quality
            - Completeness
            
            Provide improved version and quality score (0-1).
            """
            
            llm_response = self.simulate_llm_call(review_prompt, {
                "review_criteria": "comprehensive quality check",
                "agent_type": "review"
            })
            
            # Improved content and quality score
            task.final_output = task.content_draft + f"""

## Quality Review Results
- **Accuracy**: High ✅
- **Clarity**: Excellent ✅
- **Completeness**: Comprehensive ✅
- **LLM Review**: {llm_response}

**Overall Quality Score**: 0.92/1.0
            """
            
            task.quality_score = 0.92
            
            logger.info(f"📝 Review completed for: {task.topic} (Score: {task.quality_score})")
            
        return task

class LLMResearchWorkflow:
    """Orchestrates the multi-agent LLM research workflow."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        if not api_key:
            api_key = os.getenv("ALINEA_API_KEY")
            if not api_key:
                raise ValueError("API key required. Set ALINEA_API_KEY environment variable.")
        
        # Initialize Alinea client
        self.alinea = RealAlineaClient(base_url=base_url, api_key=api_key)
        
        # Initialize agents
        self.research_agent = ResearchAgent("research_agent", self.alinea)
        self.analysis_agent = AnalysisAgent("analysis_agent", self.alinea)
        self.writing_agent = WritingAgent("writing_agent", self.alinea)
        self.review_agent = ReviewAgent("review_agent", self.alinea)
        
        self.agents = [
            self.research_agent,
            self.analysis_agent, 
            self.writing_agent,
            self.review_agent
        ]
    
    async def initialize(self):
        """Register all agents with Alinea."""
        logger.info("🚀 Initializing LLM Research Workflow...")
        
        for agent in self.agents:
            await agent.register()
            
        logger.info("✅ All agents registered and ready!")
    
    async def process_research_task(self, topic: str, requirements: Dict[str, Any] = None) -> ResearchTask:
        """Process a complete research task through the agent pipeline."""
        
        if requirements is None:
            requirements = {
                "depth": "comprehensive",
                "output_format": "article",
                "length": "medium",
                "tone": "professional",
                "quality_standards": "high"
            }
        
        logger.info(f"📝 Starting research workflow for: {topic}")
        
        # Create research task
        task = ResearchTask(topic=topic, requirements=requirements)
        
        try:
            # Step 1: Research
            logger.info("🔍 Phase 1: Research")
            task = await self.research_agent.research_topic(task)
            
            # Step 2: Analysis
            logger.info("📊 Phase 2: Analysis")
            task = await self.analysis_agent.analyze_research(task)
            
            # Step 3: Writing
            logger.info("✍️ Phase 3: Content Generation")
            task = await self.writing_agent.generate_content(task)
            
            # Step 4: Review
            logger.info("📝 Phase 4: Quality Review")
            task = await self.review_agent.review_content(task)
            
            logger.info(f"🎉 Research workflow completed! Quality Score: {task.quality_score}")
            
            return task
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            
            # Trace causality to understand failure
            await self.trace_failure_causality(str(e))
            raise
    
    async def trace_failure_causality(self, error_description: str):
        """Trace causality when workflow fails."""
        try:
            logger.info("🔍 Tracing failure causality...")
            
            causal_path = await self.alinea.trace_causality(f"workflow_failure_{error_description}")
            
            logger.info(f"📊 Causal analysis found {len(causal_path.path)} causal steps:")
            for i, node in enumerate(causal_path.path):
                logger.info(f"  {i+1}. {node.event} (confidence: {node.confidence})")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not trace causality: {e}")
    
    async def get_workflow_insights(self):
        """Get insights about the workflow performance."""
        try:
            # Get adaptation metrics
            metrics = await self.alinea.get_adaptation_metrics()
            logger.info(f"📈 Workflow Metrics:")
            logger.info(f"  - Success Rate: {metrics.success_rate}")
            logger.info(f"  - Avg Response Time: {metrics.avg_response_time_ms}ms")
            
            # Get pattern confidence
            for agent in self.agents:
                confidence = await self.alinea.get_pattern_confidence(f"{agent.agent_id}_patterns")
                logger.info(f"  - {agent.agent_id} Confidence: {confidence.confidence}")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not get insights: {e}")
    
    async def cleanup(self):
        """Clean up resources."""
        logger.info("🧹 Cleaning up workflow...")
        
        for agent in self.agents:
            try:
                await self.alinea.unregister_agent(agent.agent_id)
            except Exception as e:
                logger.warning(f"⚠️ Could not unregister {agent.agent_id}: {e}")
        
        if hasattr(self.alinea, 'close'):
            await self.alinea.close()

# Example usage and demonstration
async def main():
    """Demonstrate the LLM Research Workflow."""
    
    logger.info("🚀 Starting LLM-Based Research & Writing Assistant Demo")
    
    # Check API key
    api_key = os.getenv("ALINEA_API_KEY")
    if not api_key:
        logger.error("❌ ALINEA_API_KEY environment variable not set")
        logger.error("   Set it with: export ALINEA_API_KEY=your_api_key_here")
        return
    
    workflow = None
    
    try:
        # Initialize workflow
        workflow = LLMResearchWorkflow(
            base_url="http://localhost:8000",
            api_key=api_key
        )
        
        await workflow.initialize()
        
        # Demo 1: Technology Research
        logger.info("\n" + "="*60)
        logger.info("📖 DEMO 1: AI Technology Research")
        logger.info("="*60)
        
        tech_task = await workflow.process_research_task(
            topic="The Future of AI in Healthcare",
            requirements={
                "depth": "comprehensive",
                "output_format": "research_report",
                "length": "long",
                "tone": "professional",
                "quality_standards": "high"
            }
        )
        
        print("\n" + "="*60)
        print("📄 RESEARCH REPORT OUTPUT:")
        print("="*60)
        print(tech_task.final_output)
        
        # Demo 2: Business Analysis
        logger.info("\n" + "="*60)
        logger.info("📊 DEMO 2: Business Analysis")
        logger.info("="*60)
        
        business_task = await workflow.process_research_task(
            topic="Remote Work Impact on Corporate Culture",
            requirements={
                "depth": "standard",
                "output_format": "executive_summary",
                "length": "medium",
                "tone": "business",
                "quality_standards": "high"
            }
        )
        
        print("\n" + "="*60)
        print("📊 BUSINESS ANALYSIS OUTPUT:")
        print("="*60)
        print(business_task.final_output)
        
        # Get workflow insights
        logger.info("\n" + "="*60)
        logger.info("📈 WORKFLOW PERFORMANCE INSIGHTS")
        logger.info("="*60)
        
        await workflow.get_workflow_insights()
        
        logger.info("\n🎉 LLM Research Workflow Demo Complete!")
        logger.info("✅ All agents coordinated successfully using Alinea")
        logger.info("✅ Memory-first coordination demonstrated")
        logger.info("✅ Causality tracing available for debugging")
        logger.info("✅ Secure API key management implemented")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        if workflow:
            await workflow.trace_failure_causality(str(e))
        
    finally:
        if workflow:
            await workflow.cleanup()

# Additional utility functions for extending the workflow

def create_custom_research_requirements(
    research_depth: str = "standard",
    output_format: str = "article", 
    content_length: str = "medium",
    tone: str = "professional",
    quality_standards: str = "high",
    include_citations: bool = True,
    fact_check_level: str = "standard"
) -> Dict[str, Any]:
    """Helper function to create custom research requirements."""
    
    return {
        "depth": research_depth,
        "output_format": output_format,
        "length": content_length,
        "tone": tone,
        "quality_standards": quality_standards,
        "include_citations": include_citations,
        "fact_check_level": fact_check_level
    }

async def batch_research_workflow(topics: List[str], base_requirements: Dict[str, Any] = None):
    """Process multiple research topics in batch."""
    
    workflow = LLMResearchWorkflow()
    await workflow.initialize()
    
    results = []
    
    try:
        for topic in topics:
            logger.info(f"🔄 Processing: {topic}")
            task = await workflow.process_research_task(topic, base_requirements)
            results.append(task)
            
        return results
        
    finally:
        await workflow.cleanup()

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())