# Global News Room Usage Examples

This document provides practical examples of using the Global News Room workflow for multi-perspective news analysis.

## Basic Usage

After setting up your environment variables and installing the workflow, you can run it with:

```bash
aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input "Your news topic here"
```

## Example Queries

### 1. Geopolitical Events

**US-China Relations:**
```bash
aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input "Latest US-China trade negotiations and tariff discussions"
```

**Taiwan Strait Tensions:**
```bash
aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input "Recent developments in Taiwan Strait military exercises"
```

**Ukraine Conflict:**
```bash
aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input "Current status of Ukraine conflict and peace negotiations"
```

### 2. Economic & Technology

**Global Chip Industry:**
```bash
aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input "Semiconductor industry competition between US and China"
```

**AI Development:**
```bash
aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input "AI regulation developments in US vs China"
```

**Climate Policy:**
```bash
aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input "Climate change policies and renewable energy investments globally"
```

### 3. Regional Issues

**South China Sea:**
```bash
aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input "South China Sea territorial disputes and ASEAN response"
```

**Middle East Relations:**
```bash
aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input "China's role in Middle East diplomacy and peace initiatives"
```

**European Union Policy:**
```bash
aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input "EU strategic autonomy vis-à-vis US and China"
```

## Expected Output Structure

Each query will return a comprehensive analysis with these sections:

### 📰 Executive Summary
Brief overview of the topic and why it matters globally

### 📅 Key Facts & Timeline
- Verified facts from multiple sources
- Chronological timeline of major events

### 🔍 Perspective Analysis

**Western/English-Language Perspective:**
- Main narrative and framing
- Key concerns and priorities
- Official positions of major Western governments

**Chinese Perspective:**
- Chinese narrative and framing
- Key concerns and priorities
- Official Chinese government position

**Other Regional Perspectives:**
- EU, ASEAN, African Union, etc. (when relevant)
- Emerging market viewpoints

### ⚡ Critical Disagreements
- Point-by-point comparison of conflicting interpretations
- Factual disputes vs. interpretive differences
- What each side claims the other is missing

### 🔮 Implications & Outlook
- Short-term and long-term implications
- What to watch for next
- Unresolved questions

### 🔍 Information Reliability
- Source credibility assessment
- Potential biases to consider
- Information gaps and limitations

## Tips for Better Results

### 1. Be Specific
Instead of: "China news"
Use: "China's latest economic policies affecting international trade"

### 2. Current Topics Work Best
The workflow excels with recent events that have active coverage in both English and Chinese media.

### 3. Controversial Topics Provide Rich Analysis
Topics where Western and Chinese perspectives differ significantly will yield the most interesting comparative analysis.

### 4. Include Context
Adding timeframes or specific aspects can improve results:
- "Ukraine conflict developments in the past month"
- "Taiwan semiconductor industry impact on global supply chains"

## Troubleshooting Examples

If you get limited results, try:

1. **Make the topic more current:**
   - "Recent" or "latest" or "2024" in your query

2. **Add geopolitical context:**
   - "How does [topic] affect US-China relations?"

3. **Be more specific:**
   - Instead of "AI", use "AI chip export controls between US and China"

## Advanced Usage

### Custom Configuration

You can modify the agent prompts in the config file to:
- Focus on specific regions beyond US/China
- Adjust the analysis framework
- Change the synthesis structure

### Batch Processing

For multiple related queries, you can create a simple script:

```bash
#!/bin/bash
topics=(
    "US-China trade war latest developments"
    "Taiwan semiconductor industry updates" 
    "China Belt and Road Initiative progress"
)

for topic in "${topics[@]}"; do
    echo "Analyzing: $topic"
    aiq run --config_file global_news_room/src/global_news_room/configs/config.yml --input "$topic" > "analysis_${topic// /_}.md"
done
```

This creates separate analysis files for each topic.

## Real-World Use Cases

### For Journalists
- Get comprehensive background before interviewing sources
- Understand how the same story is covered in different regions
- Identify gaps in your own coverage

### For Analysts
- Rapid situational awareness on developing stories
- Understanding cultural context behind different narratives
- Identifying information warfare and propaganda patterns

### For Students & Researchers
- Compare how different media systems frame the same events
- Study bias and perspective in international journalism
- Research cross-cultural communication challenges

### For Business
- Assess geopolitical risks for international operations
- Understand regulatory environments across different regions
- Monitor sentiment and policy trends affecting global markets 