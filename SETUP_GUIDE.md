# AIML API Documentation Scraper - Setup Guide for Termux

## Overview

This pipeline scrapes AIML API documentation for any specified model and generates a comprehensive `context.md` file that you can share with AI assistants for script development and API integration.

## Quick Start

### Prerequisites

- **Termux** (Android terminal emulator)
- **Internet connection**
- **Basic shell knowledge**

### Installation Steps

#### 1. Install Required Packages

```bash
# Update package manager
pkg update && pkg upgrade -y

# Install dependencies
pkg install -y curl jq python3 git

# Install Python packages
pip install requests beautifulsoup4
```

#### 2. Download the Scripts

Option A: Clone from GitHub (if available)
```bash
git clone https://github.com/yourusername/aiml-scraper.git
cd aiml-scraper
```

Option B: Manual setup
```bash
# Create project directory
mkdir -p ~/aiml-scraper
cd ~/aiml-scraper

# Copy scripts here
# (transfer files to Termux)
```

#### 3. Make Scripts Executable

```bash
chmod +x aiml_scraper.sh
chmod +x aiml_advanced_scraper.py
```

#### 4. Set Up API Key (Optional but Recommended)

```bash
# Add to ~/.bashrc or ~/.profile
echo 'export AIML_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

---

## Usage

### Basic Usage - Bash Script

```bash
# Simple usage
./aiml_scraper.sh gpt-4o

# Output goes to: ./aiml_context/context.md
```

### Advanced Usage - Python Script

```bash
# Using Python for better extraction
python3 aiml_advanced_scraper.py gpt-4o

# With custom output directory
python3 aiml_advanced_scraper.py gpt-4o ./my_docs
```

### Supported Models

The scraper automatically detects the provider based on model prefix:

| Prefix | Provider | Examples |
|--------|----------|----------|
| `gpt-` | OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo |
| `o1`, `o3`, `o4` | OpenAI | o1, o3-mini, o4-mini |
| `claude-` | Anthropic | claude-3-sonnet, claude-3-opus |
| `deepseek-` | DeepSeek | deepseek-chat, deepseek-coder |
| `gemini-` | Google | gemini-2.0-flash, gemini-pro |
| `mistral-` | Mistral AI | mistral-large, mistral-small |
| `llama-` | Meta | llama-2-70b |
| `qwen-` | Alibaba | qwen-max, qwen-turbo |
| `moonshot-` | Moonshot | moonshot-v1 |
| `command-` | Cohere | command-r-plus |
| `grok-` | xAI | grok-2 |

### Example Commands

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
python3 aiml_advanced_scraper.py claude-3-sonnet ./my_context
```

---

## Output Structure

After running the scraper, you'll get:

```
aiml_context/
├── context.md              # Main output file (share this with AI)
├── cache/                  # Cached HTML files
│   ├── [hash1].html
│   ├── [hash2].html
│   └── ...
└── temp/                   # Temporary files
    ├── gpt-4o_raw.html
    └── gpt-4o_extracted.txt
```

### The context.md File

This file contains:
- ✅ Model overview and description
- ✅ Complete authentication setup
- ✅ All API endpoints
- ✅ Request parameters (required & optional)
- ✅ Response format examples
- ✅ Code examples (Python, JavaScript, cURL, Bash)
- ✅ Error handling strategies
- ✅ Rate limiting information
- ✅ Cost optimization tips
- ✅ Termux-specific examples

---

## Advanced Usage

### Running Multiple Models

```bash
#!/bin/bash
# Save as: scrape_multiple.sh

models=("gpt-4o" "gpt-4o-mini" "claude-3-sonnet" "deepseek-chat")

for model in "${models[@]}"; do
    echo "Scraping $model..."
    python3 aiml_advanced_scraper.py "$model" "./docs_$model"
    echo "Done: $model"
    sleep 2  # Be nice to servers
done
```

Run with:
```bash
chmod +x scrape_multiple.sh
./scrape_multiple.sh
```

### Caching Strategy

The scraper caches downloaded HTML to avoid repeated requests:

```bash
# Use cache (default)
python3 aiml_advanced_scraper.py gpt-4o

# Force refresh (clear cache first)
rm -rf aiml_context/cache
python3 aiml_advanced_scraper.py gpt-4o
```

### Sharing with AI Assistants

1. **Generate context file**:
   ```bash
   python3 aiml_advanced_scraper.py gpt-4o
   ```

2. **View the file**:
   ```bash
   cat aiml_context/context.md
   ```

3. **Share with AI**:
   - Copy the entire `context.md` file
   - Paste into your AI assistant conversation
   - Ask it to help build scripts/pipelines using this context

4. **Example prompt for AI**:
   ```
   I have documentation context for the AIML API (gpt-4o model).
   
   [Paste context.md here]
   
   Can you help me:
   1. Build a script that calls this API
   2. Implement error handling and retries
   3. Add streaming support
   4. Optimize for cost
   ```

---

## Troubleshooting

### Issue: "Command not found" errors

**Solution**: Install missing packages
```bash
pkg install -y curl jq python3
pip install requests beautifulsoup4
```

### Issue: "Failed to fetch" errors

**Solutions**:
- Check internet connection: `ping google.com`
- Try again (servers might be busy)
- Clear cache and retry:
  ```bash
  rm -rf aiml_context/cache
  python3 aiml_advanced_scraper.py gpt-4o
  ```

### Issue: "Model not found" errors

**Solutions**:
- Check model name spelling
- Verify model prefix is supported
- Try a known model first: `gpt-4o`
- Check if model exists on https://docs.aimlapi.com

### Issue: Empty or incomplete context.md

**Solutions**:
- Documentation site might have changed
- Try a different model
- Check raw HTML file: `cat aiml_context/temp/model_raw.html`
- Report issue with model name and error

### Issue: Storage space

**Solution**: Clear cache if running low on space
```bash
rm -rf aiml_context/cache
rm -rf aiml_context/temp
```

---

## Performance Tips

### For Termux on Limited Devices

1. **Use bash script instead of Python** (lighter):
   ```bash
   ./aiml_scraper.sh gpt-4o
   ```

2. **Clear cache regularly**:
   ```bash
   rm -rf aiml_context/cache
   ```

3. **Limit concurrent operations**:
   ```bash
   # Run one at a time, not in parallel
   ./aiml_scraper.sh gpt-4o
   ./aiml_scraper.sh claude-3-sonnet
   ```

4. **Use smaller models for testing**:
   ```bash
   # Test with gpt-4o-mini first
   ./aiml_scraper.sh gpt-4o-mini
   ```

---

## Integration with Other Tools

### Using with Cline (Cursor AI)

1. Generate context:
   ```bash
   python3 aiml_advanced_scraper.py gpt-4o
   ```

2. In Cline, add to system prompt:
   ```
   Here is AIML API documentation context:
   [Paste context.md]
   
   Use this to help me build scripts.
   ```

### Using with Continue.dev

1. Generate context for your model
2. Add to Continue.dev custom instructions
3. Reference in your prompts

### Using with LiteLLM

1. Generate context for models you want to use
2. Reference in LiteLLM configuration
3. Use for debugging integration issues

---

## Automation

### Schedule Regular Updates

Create a cron job (on Linux/macOS) or task scheduler:

```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * cd ~/aiml-scraper && python3 aiml_advanced_scraper.py gpt-4o >> ~/aiml-scraper/logs.txt 2>&1
```

### Backup Context Files

```bash
#!/bin/bash
# Save as: backup_contexts.sh

BACKUP_DIR="~/aiml-backups/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"
cp -r aiml_context/context.md "$BACKUP_DIR/"
echo "Backup created: $BACKUP_DIR"
```

---

## Advanced Configuration

### Custom Output Directory

```bash
# Python script
python3 aiml_advanced_scraper.py gpt-4o ~/my_custom_docs

# Bash script (modify script or use environment variable)
OUTPUT_DIR=~/my_docs ./aiml_scraper.sh gpt-4o
```

### Modifying Scripts

Both scripts are well-commented and can be customized:

- **aiml_scraper.sh**: Bash version, easier to modify
- **aiml_advanced_scraper.py**: Python version, more powerful extraction

Edit the `AIML_DOCS_BASE` URL if documentation moves.

---

## FAQ

**Q: Is this legal?**
A: Yes, scraping public documentation for personal use is generally legal. Always check the website's robots.txt and terms of service.

**Q: Will this get me blocked?**
A: The scraper uses reasonable delays and caching. It shouldn't cause issues. If concerned, add delays between requests.

**Q: Can I automate this?**
A: Yes! See the Automation section above.

**Q: What if the documentation changes?**
A: The scripts are designed to adapt. If they break, update the provider mapping in the script.

**Q: Can I use this on other documentation sites?**
A: Yes, but you'd need to modify the scripts for different HTML structures.

**Q: How often should I update?**
A: Run when you need fresh documentation, or set up daily/weekly automation.

---

## Support & Contribution

- **Issues**: Check troubleshooting section above
- **Improvements**: Modify scripts as needed
- **Sharing**: Feel free to share with other developers

---

## License

These scripts are provided as-is for educational and development purposes.

---

## Quick Reference

```bash
# Install
pkg update && pkg upgrade -y
pkg install -y curl jq python3
pip install requests beautifulsoup4

# Setup
cd ~/aiml-scraper
chmod +x *.sh
chmod +x *.py

# Run
./aiml_scraper.sh gpt-4o
# OR
python3 aiml_advanced_scraper.py gpt-4o

# View output
cat aiml_context/context.md

# Share with AI
# Copy aiml_context/context.md and paste into AI chat
```

---

**Last Updated**: 2025-12-10
**Version**: 1.0
**Compatible with**: Termux on Android, Linux, macOS
