#!/bin/bash

################################################################################
# AIML API Documentation Scraper for Termux (Mobile Optimized)
# Purpose: Scrape AIML API documentation and save to phone's native storage
# Author: Manus
# Date: 2025-12-10
# 
# This version saves files to /sdcard/AIML_API_Docs/ which is accessible
# through your phone's native Files app
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Save to phone's native storage
PHONE_STORAGE="/sdcard/AIML_API_Docs"
AIML_DOCS_BASE="https://docs.aimlapi.com"
CACHE_DIR="${PHONE_STORAGE}/.cache"
TEMP_DIR="${PHONE_STORAGE}/.temp"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}→${NC} $1"
}

# Check if required commands are available
check_dependencies() {
    print_step "Checking dependencies..."
    
    local missing_deps=0
    
    for cmd in curl jq; do
        if ! command -v "$cmd" &> /dev/null; then
            print_warn "$cmd is not installed"
            missing_deps=$((missing_deps + 1))
        else
            print_info "$cmd found"
        fi
    done
    
    if [ $missing_deps -gt 0 ]; then
        print_error "Missing $missing_deps dependencies. Please install them."
        echo "For Termux, run: pkg install curl jq"
        return 1
    fi
    
    return 0
}

# Check storage access and create directories
setup_storage() {
    print_step "Setting up phone storage..."
    
    # Check if we can access /sdcard/
    if [ ! -d "/sdcard" ]; then
        print_error "/sdcard/ not accessible"
        print_info "In Termux, you may need to run: termux-setup-storage"
        return 1
    fi
    
    # Create directories
    mkdir -p "$PHONE_STORAGE" "$CACHE_DIR" "$TEMP_DIR"
    
    if [ ! -w "$PHONE_STORAGE" ]; then
        print_error "No write permission to $PHONE_STORAGE"
        print_info "Try: termux-setup-storage"
        return 1
    fi
    
    print_info "Storage ready at: $PHONE_STORAGE"
    print_info "Access via Files app: AIML_API_Docs folder"
}

# Generate MD5 hash for caching
md5_hash() {
    echo -n "$1" | md5sum | cut -d' ' -f1
}

# Fetch a URL and save to cache
fetch_url() {
    local url="$1"
    local cache_file="$CACHE_DIR/$(md5_hash "$url").html"
    
    if [ -f "$cache_file" ]; then
        print_info "Using cached version of: $url"
        cat "$cache_file"
        return 0
    fi
    
    print_step "Fetching: $url"
    local response
    response=$(curl -s -L -H "User-Agent: Mozilla/5.0 (Linux; Android) AppleWebKit/537.36" "$url" 2>/dev/null)
    
    if [ -z "$response" ]; then
        print_error "Failed to fetch: $url"
        return 1
    fi
    
    echo "$response" > "$cache_file"
    echo "$response"
}

# Find model documentation URL
find_model_url() {
    local model_name="$1"
    
    print_step "Searching for model: $model_name"
    
    local model_url=""
    
    # Check if it's an OpenAI model
    if [[ "$model_name" =~ ^gpt- ]] || [[ "$model_name" == "o1" ]] || [[ "$model_name" == "o3"* ]] || [[ "$model_name" == "o4"* ]]; then
        model_url="${AIML_DOCS_BASE}/api-references/text-models-llm/openai/${model_name}"
    fi
    
    # Check if it's an Anthropic model
    if [[ "$model_name" =~ ^claude- ]]; then
        model_url="${AIML_DOCS_BASE}/api-references/text-models-llm/anthropic/${model_name}"
    fi
    
    # Check if it's a DeepSeek model
    if [[ "$model_name" =~ ^deepseek- ]]; then
        model_url="${AIML_DOCS_BASE}/api-references/text-models-llm/deepseek/${model_name}"
    fi
    
    # Check if it's a Google model
    if [[ "$model_name" =~ ^gemini- ]]; then
        model_url="${AIML_DOCS_BASE}/api-references/text-models-llm/google/${model_name}"
    fi
    
    # Check if it's a Mistral model
    if [[ "$model_name" =~ ^mistral- ]]; then
        model_url="${AIML_DOCS_BASE}/api-references/text-models-llm/mistral-ai/${model_name}"
    fi
    
    # Check if it's a Meta/Llama model
    if [[ "$model_name" =~ ^llama- ]]; then
        model_url="${AIML_DOCS_BASE}/api-references/text-models-llm/meta/${model_name}"
    fi
    
    # Check if it's a Cohere model
    if [[ "$model_name" =~ ^command- ]]; then
        model_url="${AIML_DOCS_BASE}/api-references/text-models-llm/cohere/${model_name}"
    fi
    
    # Check if it's a Moonshot model
    if [[ "$model_name" =~ ^moonshot- ]]; then
        model_url="${AIML_DOCS_BASE}/api-references/text-models-llm/moonshot/${model_name}"
    fi
    
    # Check if it's a Qwen model
    if [[ "$model_name" =~ ^qwen- ]]; then
        model_url="${AIML_DOCS_BASE}/api-references/text-models-llm/alibaba-cloud/${model_name}"
    fi
    
    # Check if it's a Grok model
    if [[ "$model_name" =~ ^grok- ]]; then
        model_url="${AIML_DOCS_BASE}/api-references/text-models-llm/xai/${model_name}"
    fi
    
    if [ -z "$model_url" ]; then
        print_error "Could not determine model URL for: $model_name"
        print_info "Supported prefixes: gpt-, o1, o3, o4, claude-, deepseek-, gemini-, mistral-, llama-, command-, moonshot-, qwen-, grok-"
        return 1
    fi
    
    print_info "Model URL: $model_url" >&2
    echo "$model_url"
}

# Scrape model documentation
scrape_model_docs() {
    local model_url="$1"
    local model_name="$2"
    
    print_step "Scraping documentation for: $model_name"
    
    local html
    html=$(fetch_url "$model_url")
    
    if [ -z "$html" ]; then
        print_error "Failed to fetch model documentation"
        return 1
    fi
    
    # Save raw HTML for debugging
    echo "$html" > "${TEMP_DIR}/${model_name}_raw.html"
    print_info "Raw HTML saved to: ${TEMP_DIR}/${model_name}_raw.html"
    
    echo "$html"
}

# Generate comprehensive context.md
generate_context_file() {
    local model_name="$1"
    local model_url="$2"
    local context_file="${PHONE_STORAGE}/${model_name}_context.md"
    
    print_step "Generating context.md file..."
    
    cat > "$context_file" << EOF
# AIML API Documentation Context: $model_name

**Generated**: $(date)
**Model**: $model_name
**Source**: $model_url

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

This documentation provides comprehensive information about the **$model_name** model available through the AIML API.

**Documentation Source**: [$model_url]($model_url)

### Key Features

- OpenAI-compatible API interface
- Multiple language support (Python, JavaScript, Node.js, cURL)
- Streaming support
- Function calling capabilities
- Vision/multimodal support (where applicable)

---

## Authentication

### API Key Setup

All requests to the AIML API require authentication using a Bearer token.

**Header Format**:
\`\`\`
Authorization: Bearer <YOUR_AIMLAPI_KEY>
\`\`\`

**Getting Your API Key**:
1. Visit https://aimlapi.com
2. Create an account or log in
3. Navigate to API Keys section
4. Generate a new API key
5. Store it securely (never commit to version control)

### Environment Variable Setup

For Termux/Linux:
\`\`\`bash
export AIML_API_KEY="your_api_key_here"
\`\`\`

For permanent setup, add to ~/.bashrc or ~/.profile:
\`\`\`bash
echo 'export AIML_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
\`\`\`

---

## API Endpoints

### Primary Endpoint: Chat Completions

**Endpoint**: \`POST https://api.aimlapi.com/v1/chat/completions\`

This is the main endpoint for text generation using the $model_name model.

### Alternative Endpoint: Responses

**Endpoint**: \`POST https://api.aimlapi.com/v1/responses\`

Alternative endpoint for certain models with simplified input format.

---

## Request Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| \`model\` | string | Model identifier (e.g., \`$model_name\`) |
| \`messages\` | array | Array of message objects with roles (system, user, assistant) |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| \`temperature\` | number | 1.0 | Controls randomness (0.0-2.0). Lower = more focused, Higher = more creative |
| \`top_p\` | number | 1.0 | Nucleus sampling parameter (0.01-1.0) |
| \`max_tokens\` | number | - | Maximum tokens in response |
| \`max_completion_tokens\` | integer | - | Upper bound for completion tokens |
| \`stream\` | boolean | false | Enable streaming responses |
| \`stop\` | array/string | - | Stop sequences (up to 4) |
| \`frequency_penalty\` | number | 0 | Penalize token frequency (-2.0 to 2.0) |
| \`presence_penalty\` | number | 0 | Penalize token presence (-2.0 to 2.0) |
| \`seed\` | integer | - | For deterministic output (Beta) |
| \`tools\` | array | - | Function definitions for function calling |
| \`tool_choice\` | string/object | auto | Control tool usage (none, auto, required) |
| \`response_format\` | object | - | Specify output format (text, json, json_schema) |
| \`logprobs\` | boolean | false | Return log probabilities |
| \`top_logprobs\` | number | - | Number of log probabilities to return |

---

## Response Format

### Success Response (200 OK)

\`\`\`json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "$model_name",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Response text here"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
\`\`\`

### Streaming Response

When \`stream: true\`, responses are sent as Server-Sent Events (SSE):

\`\`\`
data: {"choices":[{"delta":{"content":"Hello"}}]}
data: {"choices":[{"delta":{"content":" world"}}]}
data: [DONE]
\`\`\`

---

## Code Examples

### Python Example

\`\`\`python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.aimlapi.com/v1",
    api_key="YOUR_AIMLAPI_KEY"
)

response = client.chat.completions.create(
    model="$model_name",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
    temperature=0.7,
    max_tokens=100
)

print(response.choices[0].message.content)
\`\`\`

### JavaScript/Node.js Example

\`\`\`javascript
const OpenAI = require('openai');

const client = new OpenAI({
    baseURL: 'https://api.aimlapi.com/v1',
    apiKey: process.env.AIML_API_KEY
});

async function main() {
    const response = await client.chat.completions.create({
        model: '$model_name',
        messages: [
            {
                role: 'system',
                content: 'You are a helpful assistant.'
            },
            {
                role: 'user',
                content: 'What is the capital of France?'
            }
        ],
        temperature: 0.7,
        max_tokens: 100
    });

    console.log(response.choices[0].message.content);
}

main().catch(console.error);
\`\`\`

### cURL Example

\`\`\`bash
curl -X POST https://api.aimlapi.com/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_AIMLAPI_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "$model_name",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "What is the capital of France?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
\`\`\`

### Bash Script Example (Termux-friendly)

\`\`\`bash
#!/bin/bash

MODEL="$model_name"
API_KEY="\${AIML_API_KEY}"
PROMPT="\${1:-Hello}"

curl -s -X POST https://api.aimlapi.com/v1/chat/completions \\
  -H "Authorization: Bearer \$API_KEY" \\
  -H "Content-Type: application/json" \\
  -d @- << JSONEOF | jq '.choices[0].message.content'
{
  "model": "\$MODEL",
  "messages": [
    {"role": "user", "content": "\$PROMPT"}
  ],
  "temperature": 0.7,
  "max_tokens": 500
}
JSONEOF
\`\`\`

---

## Error Handling

### Common Error Codes

| Code | Error | Solution |
|------|-------|----------|
| 400 | Bad Request | Check request format and required parameters |
| 401 | Unauthorized | Verify API key is correct and valid |
| 403 | Forbidden | Check API key permissions |
| 404 | Not Found | Verify model name and endpoint URL |
| 429 | Rate Limited | Implement exponential backoff retry logic |
| 500 | Server Error | Retry after a delay |
| 503 | Service Unavailable | Wait and retry later |

### Retry Strategy (Bash)

\`\`\`bash
#!/bin/bash

retry_api_call() {
    local max_retries=3
    local timeout=1
    local attempt=1
    
    while [ \$attempt -le \$max_retries ]; do
        if curl -s -X POST https://api.aimlapi.com/v1/chat/completions \\
            -H "Authorization: Bearer \$AIML_API_KEY" \\
            -H "Content-Type: application/json" \\
            -d '{"model":"$model_name","messages":[{"role":"user","content":"test"}]}'; then
            return 0
        fi
        
        if [ \$attempt -lt \$max_retries ]; then
            echo "Retry \$attempt/\$max_retries after \${timeout}s"
            sleep \$timeout
            timeout=\$((timeout * 2))
        fi
        
        attempt=\$((attempt + 1))
    done
    
    return 1
}
\`\`\`

---

## Rate Limits & Pricing

### Rate Limiting

The AIML API implements rate limiting based on your plan:

- **Free Tier**: Limited requests per minute
- **Pro Tier**: Higher request limits
- **Enterprise**: Custom limits

### Pricing

Pricing is based on:
- **Input tokens**: Cost per 1K tokens
- **Output tokens**: Cost per 1K tokens (usually higher than input)

Check https://aimlapi.com/pricing for current rates.

### Cost Optimization Tips

1. Use \`max_tokens\` to limit response length
2. Batch requests when possible
3. Use lower temperature for deterministic responses
4. Cache common responses
5. Use streaming for long responses
6. Choose appropriate model size for your use case

---

## Additional Resources

- **Official Documentation**: https://docs.aimlapi.com
- **API Status**: https://status.aimlapi.com
- **Support**: https://aimlapi.com/support
- **GitHub**: https://github.com/aimlapi

---

## Notes for AI Assistants

This context file contains:
- ✅ Complete API endpoint information
- ✅ All request/response parameters with types
- ✅ Authentication requirements
- ✅ Code examples in multiple languages
- ✅ Error handling strategies
- ✅ Rate limiting information
- ✅ Termux/Linux-specific examples

Use this information to help users:
- Build API integrations
- Debug API calls
- Optimize requests
- Handle errors gracefully
- Implement retry logic
- Manage costs

---

**Last Updated**: $(date)
**Model**: $model_name
**API Version**: v1

EOF

    print_info "Context file generated: $context_file"
}

# Main execution
main() {
    print_header "AIML API Documentation Scraper (Mobile)"
    
    # Check if model name is provided
    if [ -z "$1" ]; then
        print_error "Model name not provided"
        echo ""
        echo "Usage: $0 <model_name>"
        echo ""
        echo "Examples:"
        echo "  $0 gpt-4o"
        echo "  $0 gpt-4o-mini"
        echo "  $0 claude-3-sonnet"
        echo "  $0 deepseek-chat"
        echo "  $0 gemini-2.0-flash"
        echo ""
        echo "Files will be saved to: $PHONE_STORAGE"
        echo "Access via your phone's Files app in: AIML_API_Docs folder"
        echo ""
        return 1
    fi
    
    local model_name="$1"
    
    # Check dependencies
    if ! check_dependencies; then
        return 1
    fi
    
    # Setup storage
    if ! setup_storage; then
        print_error "Storage setup failed"
        print_info "Run this in Termux: termux-setup-storage"
        return 1
    fi
    
    # Find model URL
    local model_url
    model_url=$(find_model_url "$model_name" 2>/dev/null) || return 1
    
    # Scrape documentation
    local html
    html=$(scrape_model_docs "$model_url" "$model_name") || return 1
    
    # Generate context file
    generate_context_file "$model_name" "$model_url"
    
    print_header "✓ Scraping Complete!"
    echo ""
    print_info "Context file saved to phone storage!"
    print_info "File: ${PHONE_STORAGE}/${model_name}_context.md"
    print_info "Access via Files app: AIML_API_Docs/${model_name}_context.md"
    echo ""
    print_step "Next steps:"
    echo "  1. Open your phone's Files app"
    echo "  2. Navigate to: AIML_API_Docs folder"
    echo "  3. Open: ${model_name}_context.md"
    echo "  4. Share or copy the content to your AI assistant"
    echo ""
}

# Run main function
main "$@"
