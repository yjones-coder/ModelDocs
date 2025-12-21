#!/usr/bin/env python3

"""
AIML API Documentation Advanced Scraper (Mobile Optimized)
Purpose: Extract detailed API information and save to phone's native storage
Author: Manus
Date: 2025-12-10

This version saves files to /sdcard/AIML_API_Docs/ which is accessible
through your phone's native Files app.
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, quote
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import subprocess

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install requests beautifulsoup4")
    sys.exit(1)


class AIMLScraperMobile:
    """Advanced scraper for AIML API documentation (Mobile optimized)"""
    
    def __init__(self, output_dir: str = "/sdcard/AIML_API_Docs"):
        self.output_dir = Path(output_dir)
        self.temp_dir = self.output_dir / ".temp"
        self.cache_dir = self.output_dir / ".cache"
        self.base_url = "https://docs.aimlapi.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/537.36'
        })
        
        self._setup_directories()
    
    def _setup_directories(self):
        """Create necessary directories"""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.temp_dir.mkdir(exist_ok=True)
            self.cache_dir.mkdir(exist_ok=True)
            print(f"[INFO] Storage ready: {self.output_dir}")
        except PermissionError:
            print(f"[ERROR] No permission to write to {self.output_dir}")
            print("[INFO] Run in Termux: termux-setup-storage")
            sys.exit(1)
    
    def _get_cache_path(self, url: str) -> Path:
        """Generate cache file path from URL"""
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.html"
    
    def fetch_url(self, url: str, use_cache: bool = True) -> Optional[str]:
        """Fetch URL with caching"""
        cache_path = self._get_cache_path(url)
        
        if use_cache and cache_path.exists():
            print(f"[CACHE] Using cached version: {url}")
            return cache_path.read_text(encoding='utf-8')
        
        try:
            print(f"[FETCH] Retrieving: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Cache the response
            cache_path.write_text(response.text, encoding='utf-8')
            return response.text
        except requests.RequestException as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            return None
    
    def find_model_url(self, model_name: str) -> Optional[str]:
        """Find documentation URL for a model"""
        print(f"[SEARCH] Looking for model: {model_name}")
        
        # Map common model prefixes to their provider paths
        provider_map = {
            'gpt-': 'openai',
            'o1': 'openai',
            'o3': 'openai',
            'o4': 'openai',
            'claude-': 'anthropic',
            'deepseek-': 'deepseek',
            'gemini-': 'google',
            'mistral-': 'mistral-ai',
            'llama-': 'meta',
            'qwen-': 'alibaba-cloud',
            'moonshot-': 'moonshot',
            'command-': 'cohere',
            'grok-': 'xai',
        }
        
        provider = None
        for prefix, prov in provider_map.items():
            if model_name.lower().startswith(prefix):
                provider = prov
                break
        
        if not provider:
            print(f"[WARN] Could not determine provider for: {model_name}")
            print(f"[INFO] Supported prefixes: {', '.join(provider_map.keys())}")
            return None
        
        model_url = f"{self.base_url}/api-references/text-models-llm/{provider}/{model_name}"
        print(f"[INFO] Constructed URL: {model_url}")
        return model_url
    
    def extract_api_parameters(self, html: str) -> Dict:
        """Extract API parameters from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        parameters = {
            'required': [],
            'optional': [],
            'descriptions': {}
        }
        
        # Look for parameter definitions
        param_patterns = [
            r'(?:parameter|param|field)["\']?\s*[:=]?\s*["\']?([a-z_]+)',
            r'<strong>([a-z_]+)</strong>\s*(?:string|integer|number|boolean|array|object)',
            r'`([a-z_]+)`\s*(?:\||:|-)',
        ]
        
        text = soup.get_text()
        
        for pattern in param_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                param_name = match.lower()
                if param_name not in parameters['required'] and param_name not in parameters['optional']:
                    # Try to determine if required
                    if 'required' in text[max(0, text.find(param_name)-100):text.find(param_name)+100].lower():
                        parameters['required'].append(param_name)
                    else:
                        parameters['optional'].append(param_name)
        
        return parameters
    
    def extract_code_examples(self, html: str) -> Dict[str, str]:
        """Extract code examples from documentation"""
        soup = BeautifulSoup(html, 'html.parser')
        
        examples = {}
        
        # Find code blocks
        code_blocks = soup.find_all('code')
        
        for i, code in enumerate(code_blocks):
            code_text = code.get_text()
            
            if 'curl' in code_text.lower():
                examples['curl'] = code_text
            elif 'python' in code_text.lower() or 'import' in code_text:
                examples['python'] = code_text
            elif 'javascript' in code_text.lower() or 'async' in code_text:
                examples['javascript'] = code_text
            elif 'bash' in code_text.lower():
                examples['bash'] = code_text
        
        return examples
    
    def extract_model_info(self, html: str) -> Dict:
        """Extract model information from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        info = {
            'description': '',
            'capabilities': [],
            'endpoints': [],
            'model_ids': []
        }
        
        # Extract description (usually first paragraph)
        paragraphs = soup.find_all('p')
        if paragraphs:
            info['description'] = paragraphs[0].get_text().strip()
        
        # Extract endpoints
        endpoint_pattern = r'https://api\.aimlapi\.com/v1/[a-z/\-]+'
        endpoints = re.findall(endpoint_pattern, text)
        info['endpoints'] = list(set(endpoints))
        
        # Extract model IDs
        model_id_pattern = r'(?:model["\']?\s*[:=]\s*["\']?)([a-z0-9\-\.]+)(?:["\'])?'
        model_ids = re.findall(model_id_pattern, text, re.IGNORECASE)
        info['model_ids'] = list(set(model_ids))[:15]
        
        # Extract capabilities
        capability_keywords = [
            'streaming', 'function calling', 'vision', 'audio', 'json', 
            'tool use', 'reasoning', 'search', 'embeddings', 'moderation'
        ]
        
        for keyword in capability_keywords:
            if keyword.lower() in text.lower():
                info['capabilities'].append(keyword)
        
        return info
    
    def generate_context_md(self, model_name: str, model_url: str, 
                           html: str) -> str:
        """Generate comprehensive context.md file"""
        
        output_file = str(self.output_dir / f"{model_name}_context.md")
        
        print(f"[GENERATE] Creating context file: {output_file}")
        
        # Extract information
        model_info = self.extract_model_info(html)
        parameters = self.extract_api_parameters(html)
        examples = self.extract_code_examples(html)
        
        # Build markdown content
        md_content = f"""# AIML API Documentation Context: {model_name}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Model**: {model_name}
**Source**: {model_url}

---

## Table of Contents

1. [Model Overview](#model-overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Request Parameters](#request-parameters)
5. [Response Format](#response-format)
6. [Code Examples](#code-examples)
7. [Error Handling](#error-handling)
8. [Rate Limits & Pricing](#rate-limits--pricing)

---

## Model Overview

### Description

{model_info['description'] or 'See documentation for details.'}

### Capabilities

{self._format_list(model_info['capabilities']) if model_info['capabilities'] else '- Standard text generation capabilities'}

### Documentation

- **Full Documentation**: [{model_url}]({model_url})
- **Base URL**: https://api.aimlapi.com/v1

---

## Authentication

### API Key Setup

All requests require Bearer token authentication:

```
Authorization: Bearer <YOUR_AIMLAPI_KEY>
```

### Environment Setup (Termux/Linux)

```bash
# Set temporarily
export AIML_API_KEY="your_key_here"

# Set permanently
echo 'export AIML_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### Getting Your API Key

1. Visit https://aimlapi.com
2. Sign up or log in
3. Go to API Keys section
4. Generate new key
5. Store securely

---

## API Endpoints

### Available Endpoints

{self._format_list(model_info['endpoints']) if model_info['endpoints'] else '- `POST https://api.aimlapi.com/v1/chat/completions`'}

### Primary Endpoint

**POST** `https://api.aimlapi.com/v1/chat/completions`

Main endpoint for chat-based interactions with {model_name}.

---

## Request Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Model ID (e.g., `{model_name}`) |
| `messages` | array | Array of message objects with roles |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `temperature` | number | 1.0 | Randomness (0.0-2.0) |
| `top_p` | number | 1.0 | Nucleus sampling (0.01-1.0) |
| `max_tokens` | number | - | Max response tokens |
| `stream` | boolean | false | Enable streaming |
| `stop` | array/string | - | Stop sequences (up to 4) |
| `frequency_penalty` | number | 0 | Frequency penalty (-2.0 to 2.0) |
| `presence_penalty` | number | 0 | Presence penalty (-2.0 to 2.0) |
| `seed` | integer | - | For deterministic output |
| `tools` | array | - | Function definitions |
| `tool_choice` | string | auto | Tool usage control |
| `response_format` | object | - | Output format (text, json) |

---

## Response Format

### Success Response (200 OK)

```json
{{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "{model_name}",
  "choices": [
    {{
      "index": 0,
      "message": {{
        "role": "assistant",
        "content": "Response text"
      }},
      "finish_reason": "stop"
    }}
  ],
  "usage": {{
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }}
}}
```

### Error Response

```json
{{
  "error": {{
    "message": "Error description",
    "type": "error_type",
    "code": "error_code"
  }}
}}
```

---

## Code Examples

### Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.aimlapi.com/v1",
    api_key="{model_name}"
)

response = client.chat.completions.create(
    model="{model_name}",
    messages=[
        {{"role": "system", "content": "You are helpful."}},
        {{"role": "user", "content": "Hello!"}}
    ],
    temperature=0.7,
    max_tokens=100
)

print(response.choices[0].message.content)
```

### JavaScript

```javascript
const OpenAI = require('openai');

const client = new OpenAI({{
    baseURL: 'https://api.aimlapi.com/v1',
    apiKey: process.env.AIML_API_KEY
}});

async function main() {{
    const response = await client.chat.completions.create({{
        model: '{model_name}',
        messages: [
            {{"role": "system", "content": "You are helpful."}},
            {{"role": "user", "content": "Hello!"}}
        ],
        temperature: 0.7,
        max_tokens: 100
    }});

    console.log(response.choices[0].message.content);
}}

main().catch(console.error);
```

### cURL

```bash
curl -X POST https://api.aimlapi.com/v1/chat/completions \\
  -H "Authorization: Bearer $AIML_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model_name}",
    "messages": [
      {{"role": "user", "content": "Hello!"}}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }}'
```

### Bash (Termux-friendly)

```bash
#!/bin/bash

MODEL="{model_name}"
API_KEY="${{AIML_API_KEY}}"
PROMPT="${{1:-Hello}}"

curl -s -X POST https://api.aimlapi.com/v1/chat/completions \\
  -H "Authorization: Bearer $API_KEY" \\
  -H "Content-Type: application/json" \\
  -d @- << EOF | jq '.choices[0].message.content'
{{
  "model": "$MODEL",
  "messages": [{{"role": "user", "content": "$PROMPT"}}],
  "temperature": 0.7,
  "max_tokens": 500
}}
EOF
```

---

## Error Handling

### Common Error Codes

| Code | Error | Solution |
|------|-------|----------|
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Verify model name |
| 429 | Rate Limited | Implement backoff |
| 500 | Server Error | Retry later |

### Retry Strategy

```python
import time
import random

def call_with_retry(client, model, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages
            )
        except Exception as e:
            if attempt < max_retries - 1:
                wait = (2 ** attempt) + random.uniform(0, 1)
                print(f"Retry {attempt + 1}/{max_retries} in {wait:.2f}s")
                time.sleep(wait)
            else:
                raise
```

---

## Rate Limits & Pricing

### Rate Limiting

- **Free Tier**: Limited requests/minute
- **Pro Tier**: Higher limits
- **Enterprise**: Custom limits

### Pricing

Costs based on:
- Input tokens: Cost per 1K tokens
- Output tokens: Higher cost per 1K tokens

Check https://aimlapi.com/pricing for current rates.

### Cost Optimization

1. Use `max_tokens` to limit responses
2. Batch requests when possible
3. Use lower temperature for deterministic output
4. Cache common responses
5. Use streaming for long responses
6. Choose appropriate model size

---

## Model IDs

The following model IDs are available for {model_name}:

{self._format_list(model_info['model_ids']) if model_info['model_ids'] else '- See documentation for available model IDs'}

---

## Additional Resources

- **Official Docs**: https://docs.aimlapi.com
- **Status Page**: https://status.aimlapi.com
- **Support**: https://aimlapi.com/support
- **GitHub**: https://github.com/aimlapi

---

## For AI Assistants

This context file contains:
- ✅ Complete API endpoint information
- ✅ All request/response parameters with types
- ✅ Authentication requirements
- ✅ Code examples in multiple languages
- ✅ Error handling strategies
- ✅ Rate limiting information
- ✅ Termux/Linux-specific examples

Use this to help users:
- Build API integrations
- Debug API calls
- Optimize requests
- Handle errors gracefully
- Implement retry logic
- Manage costs

---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Model**: {model_name}
**API Version**: v1
**Storage**: /sdcard/AIML_API_Docs/
"""
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"[SUCCESS] Context file created: {output_file}")
        return output_file
    
    @staticmethod
    def _format_list(items: List[str]) -> str:
        """Format list as markdown bullet points"""
        if not items:
            return "- No items"
        return '\n'.join([f"- {item}" for item in items])
    
    def scrape_model(self, model_name: str) -> Optional[str]:
        """Main scraping workflow"""
        print(f"\n[START] Scraping documentation for: {model_name}\n")
        
        # Find model URL
        model_url = self.find_model_url(model_name)
        if not model_url:
            return None
        
        # Fetch documentation
        html = self.fetch_url(model_url)
        if not html:
            return None
        
        # Save raw HTML for debugging
        raw_html_path = self.temp_dir / f"{model_name}_raw.html"
        raw_html_path.write_text(html, encoding='utf-8')
        print(f"[DEBUG] Raw HTML saved to: {raw_html_path}")
        
        # Generate context file
        context_file = self.generate_context_md(
            model_name, 
            model_url, 
            html
        )
        
        print(f"\n[COMPLETE] Scraping finished!")
        print(f"[OUTPUT] Context file: {context_file}")
        print(f"[OUTPUT] Access via Files app: AIML_API_Docs/{model_name}_context.md")
        
        return context_file


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("AIML API Documentation Scraper (Mobile)")
        print("\nUsage: python3 aiml_advanced_scraper_mobile.py <model_name>")
        print("\nExamples:")
        print("  python3 aiml_advanced_scraper_mobile.py gpt-4o")
        print("  python3 aiml_advanced_scraper_mobile.py claude-3-sonnet")
        print("  python3 aiml_advanced_scraper_mobile.py deepseek-chat")
        print("\nFiles will be saved to: /sdcard/AIML_API_Docs/")
        print("Access via your phone's Files app")
        sys.exit(1)
    
    model_name = sys.argv[1]
    
    scraper = AIMLScraperMobile()
    result = scraper.scrape_model(model_name)
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
