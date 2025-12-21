# AIML API Documentation Scraper Pipeline

A Termux-compatible pipeline for scraping AIML API documentation and generating comprehensive context files for AI assistants.

## Overview

This project provides scripts to automatically scrape AIML API documentation for any specified model and generate a `context.md` file containing:

- Complete API endpoint information
- All request/response parameters with types and descriptions
- Authentication requirements and setup
- Code examples in multiple languages (Python, JavaScript, cURL, Bash)
- Error handling strategies and retry logic
- Rate limiting and pricing information
- Termux/Linux-specific examples

## Features

✅ **Termux-Compatible**: Works on Android devices via Termux  
✅ **Multi-Language Support**: Supports 10+ model providers  
✅ **Caching**: Avoids redundant network requests  
✅ **Easy to Use**: Single command to generate documentation  
✅ **AI-Ready**: Output formatted for sharing with AI assistants  
✅ **Bash & Python**: Two implementation options  

## Quick Start

### Installation

```bash
# Install dependencies
pkg update && pkg upgrade -y
pkg install -y curl jq python3
pip install requests beautifulsoup4

# Download and setup
mkdir -p ~/aiml-scraper
cd ~/aiml-scraper
# Copy scripts here

chmod +x aiml_scraper.sh
chmod +x aiml_advanced_scraper.py
```

### Basic Usage

```bash
# Generate context for gpt-4o
./aiml_scraper.sh gpt-4o

# Output: ./aiml_context/context.md
```

### View Output

```bash
cat aiml_context/context.md
```

## Supported Models

| Provider | Prefix | Examples |
|----------|--------|----------|
| OpenAI | `gpt-`, `o1`, `o3`, `o4` | gpt-4o, o1, o3-mini |
| Anthropic | `claude-` | claude-3-sonnet, claude-3-opus |
| DeepSeek | `deepseek-` | deepseek-chat, deepseek-coder |
| Google | `gemini-` | gemini-2.0-flash, gemini-pro |
| Mistral | `mistral-` | mistral-large, mistral-small |
| Meta | `llama-` | llama-2-70b |
| Alibaba | `qwen-` | qwen-max, qwen-turbo |
| Moonshot | `moonshot-` | moonshot-v1 |
| Cohere | `command-` | command-r-plus |
| xAI | `grok-` | grok-2 |

## Usage Examples

```bash
# OpenAI models
./aiml_scraper.sh gpt-4o
./aiml_scraper.sh gpt-4o-mini
./aiml_scraper.sh o1

# Anthropic models
./aiml_scraper.sh claude-3-sonnet

# DeepSeek models
./aiml_scraper.sh deepseek-chat

# Google models
./aiml_scraper.sh gemini-2.0-flash

# Using Python scraper
python3 aiml_advanced_scraper.py gpt-4o
python3 aiml_advanced_scraper.py claude-3-sonnet ./my_docs
```

## Output Structure

```
aiml_context/
├── context.md              # Main output (share this!)
├── cache/                  # Cached HTML files
│   ├── [hash1].html
│   └── [hash2].html
└── temp/                   # Temporary files
    ├── model_raw.html
    └── model_extracted.txt
```

## Sharing with AI Assistants

1. Generate context:
   ```bash
   ./aiml_scraper.sh gpt-4o
   ```

2. Copy the context file:
   ```bash
   cat aiml_context/context.md
   ```

3. Share with AI assistant:
   - Paste the entire context.md into your AI chat
   - Ask it to help build scripts/pipelines using this context

4. Example prompt:
   ```
   I have AIML API documentation context for gpt-4o.
   
   [Paste context.md here]
   
   Can you help me:
   1. Build a script that calls this API
   2. Implement error handling and retries
   3. Add streaming support
   4. Optimize for cost
   ```

## Scripts Included

### 1. aiml_scraper.sh (Bash)
- Lightweight and fast
- No Python dependencies
- Best for Termux on limited devices
- Usage: `./aiml_scraper.sh <model_name>`

### 2. aiml_advanced_scraper.py (Python)
- More robust extraction
- Better error handling
- Supports custom output directories
- Usage: `python3 aiml_advanced_scraper.py <model_name> [output_dir]`

### 3. SETUP_GUIDE.md
- Comprehensive setup instructions
- Troubleshooting guide
- Advanced usage patterns
- Integration examples

## Advanced Usage

### Batch Processing

```bash
#!/bin/bash
# Save as: scrape_multiple.sh

models=("gpt-4o" "gpt-4o-mini" "claude-3-sonnet" "deepseek-chat")

for model in "${models[@]}"; do
    echo "Scraping $model..."
    python3 aiml_advanced_scraper.py "$model" "./docs_$model"
    sleep 2
done
```

Run with:
```bash
chmod +x scrape_multiple.sh
./scrape_multiple.sh
```

### Caching

```bash
# Use cache (default)
./aiml_scraper.sh gpt-4o

# Force refresh
rm -rf aiml_context/cache
./aiml_scraper.sh gpt-4o
```

### Environment Setup

```bash
# Add to ~/.bashrc or ~/.profile
export AIML_API_KEY="your_key_here"

# Then use in scripts
curl -H "Authorization: Bearer $AIML_API_KEY" \
  https://api.aimlapi.com/v1/chat/completions
```

## Troubleshooting

### Missing Dependencies
```bash
pkg install -y curl jq python3
pip install requests beautifulsoup4
```

### Failed to Fetch
- Check internet: `ping google.com`
- Clear cache: `rm -rf aiml_context/cache`
- Try again (servers might be busy)

### Model Not Found
- Check spelling
- Verify prefix is supported
- Try a known model first: `gpt-4o`

### Storage Issues
```bash
# Clear cache if running low on space
rm -rf aiml_context/cache
rm -rf aiml_context/temp
```

## Performance Tips

- Use bash script for limited devices
- Clear cache regularly
- Run one model at a time
- Use smaller models for testing

## Integration Examples

### With Cline (Cursor AI)
1. Generate context: `./aiml_scraper.sh gpt-4o`
2. Add to system prompt in Cline
3. Reference in your prompts

### With Continue.dev
1. Generate context for your models
2. Add to Continue.dev custom instructions
3. Reference in prompts

### With LiteLLM
1. Generate context for models you use
2. Reference in LiteLLM configuration
3. Use for debugging integration

## File Descriptions

| File | Purpose |
|------|---------|
| `aiml_scraper.sh` | Main bash scraper (recommended for Termux) |
| `aiml_advanced_scraper.py` | Advanced Python scraper with better extraction |
| `SETUP_GUIDE.md` | Comprehensive setup and troubleshooting guide |
| `README.md` | This file |

## Requirements

### Minimum
- Termux or Linux/macOS shell
- `curl` command
- Internet connection

### Recommended
- `jq` for JSON processing
- `python3` for advanced scraper
- `requests` and `beautifulsoup4` Python packages

## API Information

- **Base URL**: https://api.aimlapi.com/v1
- **Main Endpoint**: POST /chat/completions
- **Authentication**: Bearer token in Authorization header
- **Documentation**: https://docs.aimlapi.com

## License

These scripts are provided as-is for educational and development purposes.

## Support

For issues or improvements:
1. Check the SETUP_GUIDE.md troubleshooting section
2. Review script comments for customization
3. Verify model name and provider prefix
4. Check internet connectivity

## Quick Reference

```bash
# Install
pkg update && pkg upgrade -y
pkg install -y curl jq python3
pip install requests beautifulsoup4

# Setup
mkdir -p ~/aiml-scraper && cd ~/aiml-scraper
chmod +x *.sh *.py

# Run
./aiml_scraper.sh gpt-4o
# OR
python3 aiml_advanced_scraper.py gpt-4o

# View
cat aiml_context/context.md

# Share with AI
# Copy aiml_context/context.md and paste into AI chat
```

---

**Version**: 1.0  
**Last Updated**: 2025-12-10  
**Compatible**: Termux, Linux, macOS  
**Python**: 3.6+  
**Bash**: 4.0+
