import asyncio
import logging
from typing import Dict, Any

from pydantic import Field

from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


class GlobalNewsRoomFunctionConfig(FunctionBaseConfig, name="global_news_room"):
    """
    A comprehensive multi-perspective news analysis system that gathers insights from English and Chinese sources,
    analyzes different geopolitical viewpoints, and synthesizes balanced summaries highlighting global perspectives.
    """
    english_agent: str = Field(description="Name of the English news gathering agent")
    chinese_agent: str = Field(description="Name of the Chinese news gathering and translation agent") 
    analysis_agent: str = Field(description="Name of the perspective analysis and debate agent")
    synthesis_agent: str = Field(description="Name of the final synthesis agent")


@register_function(config_type=GlobalNewsRoomFunctionConfig)
async def global_news_room_function(
    config: GlobalNewsRoomFunctionConfig, builder: Builder
):
    # Get the specialized agents from the builder
    english_agent = builder.get_function(config.english_agent)
    chinese_agent = builder.get_function(config.chinese_agent)
    analysis_agent = builder.get_function(config.analysis_agent)
    synthesis_agent = builder.get_function(config.synthesis_agent)
    
    async def _response_fn(input_message: str) -> str:
        """
        Main workflow orchestration:
        1. Gather news from English and Chinese sources in parallel
        2. Analyze perspectives and identify disagreements
        3. Synthesize comprehensive multi-perspective summary
        """
        
        logger.info(f"🌍 Starting global news analysis for topic: {input_message}")
        
        try:
            # Phase 1: Parallel news gathering from English and Chinese sources
            logger.info("📰 Phase 1: Gathering news from multiple sources...")
            
            # Create enhanced prompts for each agent
            english_prompt = f"""
            Topic: {input_message}
            
            Search for the most recent and comprehensive coverage of this topic from major English-language news sources. 
            Focus on gathering diverse perspectives from different regions and stakeholders.
            Include official statements, expert analysis, and any controversies or debates.
            """
            
            chinese_prompt = f"""
            Topic: {input_message}
            
            Search for coverage of this topic from Chinese-language sources. Look for:
            1. Official Chinese government positions and statements
            2. Coverage from major Chinese news outlets
            3. Chinese social media discussions if relevant
            4. Academic or expert commentary from Chinese sources
            5. Any unique Chinese perspectives not commonly found in Western media
            
            Provide English translations of key points and explain cultural/political context where needed.
            """
            
            # Run news gathering in parallel for efficiency
            english_task = english_agent.acall_invoke(english_prompt)
            chinese_task = chinese_agent.acall_invoke(chinese_prompt)
            
            # Wait for both agents to complete
            english_results, chinese_results = await asyncio.gather(english_task, chinese_task)
            
            logger.info("✅ Phase 1 complete: News gathered from both English and Chinese sources")
            
            # Phase 2: Cross-perspective analysis and debate
            logger.info("🔍 Phase 2: Analyzing perspectives and identifying disagreements...")
            
            analysis_prompt = f"""
            Topic: {input_message}
            
            ENGLISH/WESTERN SOURCES FINDINGS:
            {english_results}
            
            CHINESE SOURCES FINDINGS:
            {chinese_results}
            
            Now analyze these two perspectives:
            1. Identify key disagreements and conflicting interpretations
            2. Compare how each side frames the issue
            3. Note what information each side emphasizes or omits
            4. Examine underlying geopolitical interests and biases
            5. Highlight factual disputes vs interpretive differences
            
            Structure your analysis to clearly show the debate between perspectives.
            """
            
            analysis_results = await analysis_agent.acall_invoke(analysis_prompt)
            
            logger.info("✅ Phase 2 complete: Cross-perspective analysis finished")
            
            # Phase 3: Final synthesis and comprehensive summary
            logger.info("📝 Phase 3: Synthesizing comprehensive multi-perspective summary...")
            
            synthesis_prompt = f"""
            Topic: {input_message}
            
            ENGLISH/WESTERN PERSPECTIVE:
            {english_results}
            
            CHINESE PERSPECTIVE:
            {chinese_results}
            
            CROSS-PERSPECTIVE ANALYSIS:
            {analysis_results}
            
            Create a comprehensive, balanced summary that gives readers the complete global picture.
            Highlight where perspectives align and where they diverge, and explain why these differences exist.
            Make this accessible while maintaining analytical depth.
            """
            
            final_summary = await synthesis_agent.acall_invoke(synthesis_prompt)
            
            logger.info("✅ Phase 3 complete: Final synthesis ready")
            logger.info("🎯 Global news analysis complete!")
            
            # Format the final output with clear structure
            output = f"""
# Global News Analysis: {input_message}

{final_summary}

---
*Analysis generated by Global News Room - Multi-perspective news analysis system*
*Sources: English-language outlets, Chinese-language outlets, cross-cultural analysis*
            """
            
            return output
            
        except Exception as e:
            logger.error(f"Error in global news room workflow: {str(e)}")
            return f"""
# Global News Analysis Error

I encountered an error while analyzing the topic "{input_message}": {str(e)}

Please check:
1. NVIDIA_API_KEY is set for NIM models
2. TAVILY_API_KEY is set for web search
3. Network connectivity is available
4. Try again with a more specific topic

Error details: {str(e)}
            """

    try:
        yield FunctionInfo.create(single_fn=_response_fn)
    except GeneratorExit:
        logger.info("Global News Room workflow exited early!")
    finally:
        logger.info("Cleaning up Global News Room workflow resources.")