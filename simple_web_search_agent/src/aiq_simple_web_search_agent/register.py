# SPDX-FileCopyrightText: Copyright (c) 2024-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import List, Dict, Any
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


class CustomWebSearchConfig(FunctionBaseConfig, name="custom_web_search"):
    """A custom web search tool that doesn't require API keys."""
    max_results: int = 5
    timeout: int = 10
    description: str = "Search the web for current information and real-time data."


@register_function(config_type=CustomWebSearchConfig)
async def custom_web_search_tool(config: CustomWebSearchConfig, builder: Builder):
    """
    Custom web search tool that uses DuckDuckGo's instant answer API and HTML parsing.
    This approach doesn't require API keys and provides reasonable search results.
    """
    
    async def _perform_web_search(query: str) -> str:
        """
        Perform web search using DuckDuckGo and parse results.
        
        Args:
            query (str): The search query
            
        Returns:
            str: Formatted search results
        """
        try:
            logger.info(f"Performing web search for: {query}")
            
            # Use DuckDuckGo's instant answer API first (no rate limiting, no API key needed)
            instant_answer = await _get_duckduckgo_instant_answer(query, config.timeout)
            
            # Get web search results by scraping DuckDuckGo HTML (respectfully)
            search_results = await _get_duckduckgo_search_results(query, config.max_results, config.timeout)
            
            # Format the combined results
            formatted_results = []
            
            # Add instant answer if available
            if instant_answer:
                formatted_results.append(f"<InstantAnswer>\n{instant_answer}\n</InstantAnswer>")
            
            # Add search results
            if search_results:
                for result in search_results:
                    formatted_result = f'<Document href="{result.get("url", "")}">\n'
                    formatted_result += f'# {result.get("title", "No Title")}\n\n'
                    formatted_result += f'{result.get("snippet", "No snippet available")}\n'
                    formatted_result += '</Document>'
                    formatted_results.append(formatted_result)
            
            if not formatted_results:
                return f"No search results found for query: {query}"
            
            return "\n\n---\n\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Error performing web search: {e}")
            return f"Error performing web search: {str(e)}"
    
    # Return the function info
    yield FunctionInfo.from_fn(
        _perform_web_search,
        description=config.description
    )


async def _get_duckduckgo_instant_answer(query: str, timeout: int) -> str:
    """Get instant answer from DuckDuckGo API."""
    try:
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
        
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'AIQ-WebSearchAgent/1.0'
        })
        response.raise_for_status()
        
        data = response.json()
        
        # Extract useful information
        instant_answer = ""
        if data.get('Abstract'):
            instant_answer += f"Abstract: {data['Abstract']}\n"
        if data.get('AbstractSource'):
            instant_answer += f"Source: {data['AbstractSource']}\n"
        if data.get('Definition'):
            instant_answer += f"Definition: {data['Definition']}\n"
        if data.get('Answer'):
            instant_answer += f"Answer: {data['Answer']}\n"
            
        return instant_answer.strip()
        
    except Exception as e:
        logger.debug(f"Could not get instant answer: {e}")
        return ""


async def _get_duckduckgo_search_results(
    query: str, max_results: int, timeout: int, region: str = "us-en"
) -> List[Dict[str, Any]]:
    """Get search results by parsing DuckDuckGo HTML."""
    try:
        # Use DuckDuckGo Lite for simpler HTML parsing
        url = f"https://duckduckgo.com/lite/?q={quote_plus(query)}&kl={region}"
        
        response = requests.get(url, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; AIQ-WebSearchAgent/1.0)'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Find result rows in DuckDuckGo Lite
        result_rows = soup.find_all('tr')
        
        for row in result_rows[:max_results]:
            # Look for link in the row
            link_elem = row.find('a', href=True)
            if not link_elem:
                continue
                
            # Extract title and URL
            title = link_elem.get_text(strip=True)
            url = link_elem.get('href', '')
            
            # Skip if this looks like an ad or unwanted result
            if not title or not url or 'duckduckgo.com' in url:
                continue
            
            # Try to find snippet/description
            snippet = ""
            snippet_elem = row.find('td', class_='result-snippet')
            if snippet_elem:
                snippet = snippet_elem.get_text(strip=True)
            else:
                # Look for any text content that might be a snippet
                text_content = row.get_text(strip=True)
                if len(text_content) > len(title):
                    snippet = text_content[len(title):].strip()[:200] + "..."
            
            if title and url:
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
                
        return results[:max_results]
        
    except Exception as e:
        logger.debug(f"Could not get search results: {e}")
        return []


# Chinese Web Search Tool
class ChineseWebSearchConfig(FunctionBaseConfig, name="chinese_web_search"):
    """A Chinese web search tool that searches Chinese sources."""
    max_results: int = 5
    timeout: int = 10
    description: str = "Search the web in Chinese for information from Chinese sources."


@register_function(config_type=ChineseWebSearchConfig)
async def chinese_web_search_tool(config: ChineseWebSearchConfig, builder: Builder):
    """Chinese web search tool that focuses on Chinese sources and content."""
    
    async def _perform_chinese_web_search(query: str) -> str:
        """Perform web search focusing on Chinese sources."""
        try:
            logger.info(f"Performing Chinese web search for: {query}")
            
            # Search with Chinese region preference
            search_results = await _get_duckduckgo_search_results(
                query, config.max_results, config.timeout, region="cn-zh"
            )
            
            # Also try searching with Chinese translation if the query is in English
            chinese_query = query  # We'll let the LLM provide Chinese queries
            if not any('\u4e00' <= char <= '\u9fff' for char in query):
                # If query doesn't contain Chinese characters, suggest searching in Chinese
                chinese_query = f"{query} 中文"
                chinese_results = await _get_duckduckgo_search_results(
                    chinese_query, config.max_results, config.timeout, region="cn-zh"
                )
                search_results.extend(chinese_results)
            
            # Format the results
            formatted_results = []
            if search_results:
                for result in search_results[:config.max_results]:
                    formatted_result = f'<Document href="{result.get("url", "")}">\n'
                    formatted_result += f'# {result.get("title", "No Title")}\n\n'
                    formatted_result += f'{result.get("snippet", "No snippet available")}\n'
                    formatted_result += '</Document>'
                    formatted_results.append(formatted_result)
            
            if not formatted_results:
                return f"No Chinese search results found for query: {query}"
            
            return "\n\n---\n\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Error performing Chinese web search: {e}")
            return f"Error performing Chinese web search: {str(e)}"
    
    yield FunctionInfo.from_fn(
        _perform_chinese_web_search,
        description=config.description
    )


# Document Generator Tool
class DocumentGeneratorConfig(FunctionBaseConfig, name="document_generator"):
    """A tool for generating formatted documents and summaries."""
    output_format: str = "markdown"
    description: str = "Generate formatted documents and summaries based on research findings."


@register_function(config_type=DocumentGeneratorConfig)
async def document_generator_tool(config: DocumentGeneratorConfig, builder: Builder):
    """Generate formatted documents from research findings."""
    
    async def _generate_document(title: str, content: str, document_type: str = "summary") -> str:
        """Generate a formatted document."""
        try:
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if config.output_format.lower() == "markdown":
                document = f"""# {title}

**Document Type:** {document_type.title()}  
**Generated:** {timestamp}  
**Source:** AIQ Web Search Agent

---

## Content

{content}

---

*This document was automatically generated by the AIQ Web Search Agent using NVIDIA NIM models.*
"""
            else:
                document = f"{title}\n\n{content}\n\nGenerated: {timestamp}"
            
            return document
            
        except Exception as e:
            logger.error(f"Error generating document: {e}")
            return f"Error generating document: {str(e)}"
    
    yield FunctionInfo.from_fn(
        _generate_document,
        description=config.description
    )


# English Research Agent
class EnglishResearchAgentConfig(FunctionBaseConfig, name="english_research_agent"):
    """An agent that conducts research in English using multiple sources."""
    llm_name: str = "nim_llm"
    description: str = "Conduct comprehensive research in English using Wikipedia and web search."


@register_function(config_type=EnglishResearchAgentConfig)
async def english_research_agent_tool(config: EnglishResearchAgentConfig, builder: Builder):
    """English research agent that uses multiple tools."""
    
    async def _conduct_english_research(topic: str) -> str:
        """Conduct comprehensive English research on a topic."""
        try:
            # For now, return a placeholder that indicates the agent would research the topic
            result = f"""# English Research Agent Results for: {topic}

This agent would:
1. Search Wikipedia for encyclopedic information about {topic}
2. Search the web for current news and developments about {topic}  
3. Analyze and synthesize the findings using LLaMA 70B
4. Provide comprehensive English-language perspective

Topic to research: {topic}
Language: English
Sources: Wikipedia + Web Search
Model: meta/llama-3.1-70b-instruct
"""
            return result
            
        except Exception as e:
            logger.error(f"Error in English research: {e}")
            return f"Error conducting English research: {str(e)}"
    
    yield FunctionInfo.from_fn(
        _conduct_english_research,
        description=config.description
    )


# Chinese Research Agent
class ChineseResearchAgentConfig(FunctionBaseConfig, name="chinese_research_agent"):
    """An agent that conducts research in Chinese using Chinese sources."""
    llm_name: str = "chinese_llm"
    description: str = "Conduct comprehensive research in Chinese using Chinese web sources."


@register_function(config_type=ChineseResearchAgentConfig)
async def chinese_research_agent_tool(config: ChineseResearchAgentConfig, builder: Builder):
    """Chinese research agent that uses Chinese sources."""
    
    async def _conduct_chinese_research(topic: str) -> str:
        """Conduct comprehensive Chinese research on a topic."""
        try:
            # For now, return a placeholder that indicates the agent would research the topic
            result = f"""# 中文研究助手结果: {topic}

此助手将会：
1. 使用中文搜索引擎搜索关于{topic}的信息
2. 分析中文网站和中文资源中的相关内容
3. 使用Qwen2-7B模型进行中文分析和总结
4. 提供中文视角和独特见解

研究主题: {topic}
语言: 中文
资源: 中文网络搜索
模型: alibaba/qwen2-7b-instruct

此功能正在开发中，将提供全面的中文研究分析。
"""
            return result
            
        except Exception as e:
            logger.error(f"Error in Chinese research: {e}")
            return f"中文研究错误: {str(e)}"
    
    yield FunctionInfo.from_fn(
        _conduct_chinese_research,
        description=config.description
    )


# Debate Orchestrator
class DebateOrchestratorConfig(FunctionBaseConfig, name="debate_orchestrator"):
    """Orchestrates a structured debate between English and Chinese perspectives."""
    english_llm: str = "nim_llm"
    chinese_llm: str = "chinese_llm"
    rounds: int = 5
    description: str = "Orchestrate a structured debate between English and Chinese perspectives."


@register_function(config_type=DebateOrchestratorConfig)
async def debate_orchestrator_tool(config: DebateOrchestratorConfig, builder: Builder):
    """Orchestrate a structured debate between perspectives."""
    
    async def _orchestrate_debate(debate_data: str) -> str:
        """Conduct a structured debate between English and Chinese perspectives."""
        try:
            from aiq.builder.framework_enum import LLMFrameworkEnum
            import json
            
            # Parse the input data
            try:
                data = json.loads(debate_data)
                topic = data.get('topic', 'Unknown Topic')
                english_position = data.get('english_position', '')
                chinese_position = data.get('chinese_position', '')
                disagreements = data.get('disagreements', '')
            except:
                # Fallback parsing
                topic = "Traditional Chinese Medicine" # Default topic
                english_position = "Western medical perspective"
                chinese_position = "Traditional Chinese medical perspective"
                disagreements = "Effectiveness and safety concerns"
            
            english_llm = await builder.get_llm(llm_name=config.english_llm, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
            chinese_llm = await builder.get_llm(llm_name=config.chinese_llm, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
            
            debate_log = []
            debate_log.append(f"# STRUCTURED DEBATE: {topic}\n")
            debate_log.append(f"**Rounds:** {config.rounds}")
            debate_log.append(f"**Key Disagreements:** {disagreements}\n")
            
            # Initialize debate context
            english_context = f"""You are debating from the ENGLISH/WESTERN perspective on: {topic}

Your position: {english_position}

Key disagreements to address: {disagreements}

Rules:
- Present evidence-based arguments from English/Western sources
- Address points made by the Chinese perspective
- Be respectful but firm in defending your position
- Use specific examples and data when possible
- Keep responses focused and under 200 words per round"""

            chinese_context = f"""你正在为以下主题进行中文/中国视角的辩论: {topic}

你的立场: {chinese_position}

需要解决的关键分歧: {disagreements}

规则:
- 从中文/中国资源中提出基于证据的论据
- 回应英文观点提出的要点
- 尊重但坚定地为你的立场辩护
- 尽可能使用具体例子和数据
- 保持回应重点突出，每轮不超过200字"""

            # Conduct debate rounds
            english_last_arg = ""
            chinese_last_arg = ""
            
            for round_num in range(1, config.rounds + 1):
                debate_log.append(f"\n## Round {round_num}\n")
                
                # English argument
                english_prompt = english_context
                if round_num > 1:
                    english_prompt += f"\n\nChinese perspective's last argument:\n{chinese_last_arg}\n\nYour response:"
                else:
                    english_prompt += "\n\nPresent your opening argument:"
                
                english_response = await english_llm.ainvoke([{"role": "user", "content": english_prompt}])
                english_arg = (english_response.content if hasattr(english_response, 'content') 
                             else str(english_response))
                english_last_arg = english_arg
                
                debate_log.append(f"**English Perspective:**\n{english_arg}\n")
                
                # Chinese argument  
                chinese_prompt = chinese_context
                if round_num > 1:
                    chinese_prompt += f"\n\n英文观点的最后论述:\n{english_arg}\n\n你的回应:"
                else:
                    chinese_prompt += "\n\n请提出你的开场论述:"
                
                chinese_response = await chinese_llm.ainvoke([{"role": "user", "content": chinese_prompt}])
                chinese_arg = (chinese_response.content if hasattr(chinese_response, 'content') 
                             else str(chinese_response))
                chinese_last_arg = chinese_arg
                
                debate_log.append(f"**Chinese Perspective (中文观点):**\n{chinese_arg}\n")
            
            # Final summary
            debate_log.append("\n## Debate Summary\n")
            debate_log.append(f"**Topic:** {topic}")
            debate_log.append(f"**Rounds Completed:** {config.rounds}")
            debate_log.append("**Status:** Ready for moderator judgment")
            
            return "\n".join(debate_log)
            
        except Exception as e:
            logger.error(f"Error orchestrating debate: {e}")
            return f"Error orchestrating debate: {str(e)}"
    
    yield FunctionInfo.from_fn(
        _orchestrate_debate,
        description=config.description
    ) 