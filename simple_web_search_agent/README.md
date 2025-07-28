# Simple Web Search Agent

A simple web search agent built using the AIQ toolkit, powered by NVIDIA's LLaMA 70B model via NIM (NVIDIA Inference Microservices). This agent can search both Wikipedia for general knowledge and the web for current information without requiring external API keys.

## Features

- **NVIDIA LLaMA 70B NIM Integration**: Uses the powerful LLaMA 70B model hosted via NVIDIA's NIM service
- **Dual Search Capabilities**: 
  - Wikipedia search for encyclopedic and factual information
  - Custom web search using DuckDuckGo (no API keys required)
- **ReAct Agent**: Uses reasoning and action patterns for intelligent tool selection
- **No External API Keys**: Only requires the provided NVIDIA API key

## Architecture

The agent uses:
- **LLM**: `meta/llama-3.1-70b-instruct` via NVIDIA NIM
- **Agent Type**: ReAct (Reasoning + Acting) agent
- **Search Tools**:
  - `wikipedia_search`: For factual, encyclopedic information
  - `custom_web_search`: For current web information using DuckDuckGo
  - `current_datetime`: For date/time information

## Installation

1. Install the AIQ toolkit with LangChain support:
```bash
uv pip install -e '.[langchain]'
```

2. Install the web search agent:
```bash
cd simple_web_search_agent
uv pip install -e .
```

## Usage

### Running the Agent

```bash
# From the simple_web_search_agent directory
aiq run --config_file configs/config.yml --input "What is the latest news about artificial intelligence?"
```

### Example Queries

**General Knowledge (Wikipedia)**:
```bash
aiq run --config_file configs/config.yml --input "Tell me about the history of machine learning"
```

**Current Information (Web Search)**:
```bash
aiq run --config_file configs/config.yml --input "What are the latest developments in NVIDIA's AI chips?"
```

**Mixed Queries**:
```bash
aiq run --config_file configs/config.yml --input "Compare the concept of neural networks with recent breakthroughs in AI"
```

## Configuration

The agent is configured via `configs/config.yml`. Key components:

### LLM Configuration
```yaml
llms:
  nim_llm:
    _type: nim
    model_name: meta/llama-3.1-70b-instruct
    api_key: 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
    temperature: 0.1
    max_tokens: 1000
```

### Search Tools
```yaml
functions:
  wikipedia_search:
    _type: wikipedia_search
    max_results: 3
    description: "Search Wikipedia for factual information..."
  
  web_search:
    _type: custom_web_search
    max_results: 5
    description: "Search the web for current information..."
```

## How It Works

1. **Query Analysis**: The LLaMA 70B model analyzes your query to understand what type of information you need

2. **Tool Selection**: Based on the query, the agent decides whether to:
   - Use Wikipedia search for historical/factual information
   - Use web search for current/real-time information
   - Get current date/time if needed

3. **Information Retrieval**: The selected tool fetches relevant information

4. **Response Generation**: The LLM synthesizes the retrieved information into a comprehensive answer

## Search Capabilities

### Wikipedia Search
- Accesses Wikipedia's vast knowledge base
- Good for: Historical facts, scientific concepts, biographies, definitions
- No API key required

### Custom Web Search
- Uses DuckDuckGo's public interfaces
- Combines instant answers with web search results
- Good for: Current events, recent news, real-time information
- No API key required (respects DuckDuckGo's terms of service)

## Example Interactions

**User**: "What is quantum computing and what are the latest breakthroughs?"

**Agent**: 
1. Uses `wikipedia_search` to get foundational information about quantum computing
2. Uses `web_search` to find recent breakthroughs and news
3. Combines both sources to provide a comprehensive answer

**User**: "What's the weather like today?"

**Agent**:
1. Uses `current_datetime` to know what "today" means
2. Uses `web_search` to find current weather information
3. Provides location-specific weather if possible

## Limitations

- Web search results depend on DuckDuckGo's availability and content
- No real-time data feeds (weather, stock prices, etc.) - relies on web search
- Wikipedia search is limited to what's available in Wikipedia
- Custom web search may be affected by changes to DuckDuckGo's structure

## Troubleshooting

### Common Issues

1. **"No search results found"**: The query might be too specific or DuckDuckGo might be temporarily unavailable
2. **NVIDIA API errors**: Check that the API key is valid and has sufficient quota
3. **Import errors**: Ensure all dependencies are installed with `uv pip install -e .`

### Debug Mode

Enable verbose logging by setting `verbose: true` in the workflow configuration or by using:
```bash
aiq run --config_file configs/config.yml --input "your query" --verbose
```

## Contributing

This is a demonstration project. Feel free to extend it with additional search sources, better parsing, or enhanced reasoning capabilities.

## License

SPDX-FileCopyrightText: Copyright (c) 2024-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0 