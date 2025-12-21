# ModelDocs Scraper Toolkit - Testing Guide

## Overview

The **Scraper Toolkit** is a modular, extensible Python library designed to scrape AI model documentation from multiple providers. It's optimized for Termux on Android and can be tested on your Pixel 9a.

**Key Features**:
- ✅ Modular architecture (one scraper per provider)
- ✅ Reusable base classes
- ✅ Intelligent content extraction
- ✅ Multiple output formats (Markdown, JSON)
- ✅ Error handling & retry logic
- ✅ Termux-optimized

---

## Installation

### Step 1: Copy Scraper to Pixel

Download `scraper_toolkit.py` and copy to your Pixel 9a:

```bash
# In Termux on your Pixel
mkdir -p ~/aiml-scraper
# Download or copy scraper_toolkit.py to ~/aiml-scraper/
```

### Step 2: Install Dependencies

```bash
# Install required packages
pip install requests beautifulsoup4

# Verify installation
python3 -c "import requests, bs4; print('✅ Dependencies installed')"
```

### Step 3: Make Executable

```bash
chmod +x ~/aiml-scraper/scraper_toolkit.py
```

---

## Quick Start

### Test 1: Display Help

```bash
cd ~/aiml-scraper
python3 scraper_toolkit.py help
```

**Expected Output**: Shows all available commands and examples

---

### Test 2: Scrape AIML API Model

```bash
python3 scraper_toolkit.py scrape --provider aimlapi --source openai --model gpt-4o
```

**What it does**:
1. Fetches documentation from AIML API
2. Extracts text, code examples, and tables
3. Saves as Markdown and JSON
4. Shows summary

**Expected Output**:
```
🚀 Starting AIML API scraper...

📄 Scraping openai/gpt-4o from AIML API...
  ✅ Saved: openai_gpt-4o_context.md
  ✅ Saved: openai_gpt-4o_data.json

============================================================
📊 SCRAPER SUMMARY
============================================================
Output Directory: /root/aiml-scraper/scraped_docs
Total Files: 2

Scraped Files:
  • openai_gpt-4o_context.md (45.2 KB)
  • openai_gpt-4o_data.json (42.1 KB)
============================================================
```

---

### Test 3: Scrape OpenAI Documentation

```bash
python3 scraper_toolkit.py scrape --provider openai
```

**What it does**:
1. Fetches OpenAI API documentation
2. Extracts all models and endpoints
3. Saves complete documentation

**Expected Output**: Similar to Test 2, with OpenAI-specific content

---

### Test 4: Scrape Anthropic Documentation

```bash
python3 scraper_toolkit.py scrape --provider anthropic
```

**Expected Output**: Anthropic Claude documentation saved

---

### Test 5: Scrape Google Gemini Documentation

```bash
python3 scraper_toolkit.py scrape --provider google
```

**Expected Output**: Google Gemini API documentation saved

---

### Test 6: Scrape DeepSeek Documentation

```bash
python3 scraper_toolkit.py scrape --provider deepseek
```

**Expected Output**: DeepSeek documentation saved

---

### Test 7: Scrape Mistral Documentation

```bash
python3 scraper_toolkit.py scrape --provider mistral
```

**Expected Output**: Mistral API documentation saved

---

### Test 8: Scrape Cohere Documentation

```bash
python3 scraper_toolkit.py scrape --provider cohere
```

**Expected Output**: Cohere API documentation saved

---

### Test 9: List All Scraped Files

```bash
python3 scraper_toolkit.py list
```

**Expected Output**: Shows all files in `~/aiml-scraper/scraped_docs/`

---

## Accessing Files on Your Phone

### Method 1: Using Termux

```bash
# View the Markdown file
cat ~/aiml-scraper/scraped_docs/openai_gpt-4o_context.md

# View the JSON file
cat ~/aiml-scraper/scraped_docs/openai_gpt-4o_data.json | head -50

# Count lines in file
wc -l ~/aiml-scraper/scraped_docs/openai_gpt-4o_context.md
```

### Method 2: Using Files App

1. Open **Files** app on your Pixel
2. Navigate to: **Internal Storage → aiml-scraper → scraped_docs**
3. Open any `.md` file with a text editor
4. Share with your AI assistant

### Method 3: Copy to Shared Storage

```bash
# Copy files to Downloads (accessible from Files app)
cp ~/aiml-scraper/scraped_docs/*.md ~/storage/downloads/

# Verify
ls -lah ~/storage/downloads/*.md
```

---

## Testing Checklist

### Basic Functionality

- [ ] Installation successful (no errors)
- [ ] Help command displays correctly
- [ ] AIML API scraper works
- [ ] OpenAI scraper works
- [ ] Anthropic scraper works
- [ ] Google scraper works
- [ ] DeepSeek scraper works
- [ ] Mistral scraper works
- [ ] Cohere scraper works

### Output Quality

- [ ] Markdown files are readable
- [ ] JSON files are valid JSON
- [ ] Code examples are extracted correctly
- [ ] Tables are formatted properly
- [ ] URLs are preserved
- [ ] File sizes are reasonable (>10 KB)

### Error Handling

- [ ] Network errors are handled gracefully
- [ ] Retry logic works (test with bad connection)
- [ ] Missing providers show helpful error
- [ ] Missing arguments show helpful error

### Performance

- [ ] Scraping completes in <30 seconds
- [ ] No memory errors on Termux
- [ ] Files are saved correctly
- [ ] Summary displays correctly

---

## Batch Testing

### Test All Providers

```bash
#!/bin/bash
# Save as test_all.sh

cd ~/aiml-scraper

echo "Testing all providers..."
echo ""

# AIML API
echo "1. Testing AIML API..."
python3 scraper_toolkit.py scrape --provider aimlapi --source openai --model gpt-4o
echo ""

# OpenAI
echo "2. Testing OpenAI..."
python3 scraper_toolkit.py scrape --provider openai
echo ""

# Anthropic
echo "3. Testing Anthropic..."
python3 scraper_toolkit.py scrape --provider anthropic
echo ""

# Google
echo "4. Testing Google..."
python3 scraper_toolkit.py scrape --provider google
echo ""

# DeepSeek
echo "5. Testing DeepSeek..."
python3 scraper_toolkit.py scrape --provider deepseek
echo ""

# Mistral
echo "6. Testing Mistral..."
python3 scraper_toolkit.py scrape --provider mistral
echo ""

# Cohere
echo "7. Testing Cohere..."
python3 scraper_toolkit.py scrape --provider cohere
echo ""

# Summary
echo "All tests completed!"
python3 scraper_toolkit.py list
```

Run it:
```bash
chmod +x test_all.sh
./test_all.sh
```

---

## Troubleshooting

### Issue: "beautifulsoup4 not installed"

**Solution**:
```bash
pip install beautifulsoup4
```

### Issue: "Connection timeout"

**Solution**:
```bash
# Check internet connection
ping 8.8.8.8

# Try again (has retry logic)
python3 scraper_toolkit.py scrape --provider openai
```

### Issue: "Permission denied"

**Solution**:
```bash
chmod +x scraper_toolkit.py
```

### Issue: "No such file or directory"

**Solution**:
```bash
# Verify file exists
ls -lah ~/aiml-scraper/scraper_toolkit.py

# Check current directory
pwd

# Navigate to correct directory
cd ~/aiml-scraper
```

### Issue: "Output directory not found"

**Solution**:
```bash
# Create directory
mkdir -p ~/aiml-scraper/scraped_docs
```

---

## Customization

### Change Output Directory

Edit `scraper_toolkit.py`:

```python
class ScraperConfig:
    def __init__(self):
        # Change this line:
        self.output_dir = Path.home() / "aiml-scraper" / "scraped_docs"
        # To:
        self.output_dir = Path("/sdcard/AIML_API_Docs")
```

### Add New Provider

Create a new scraper class:

```python
class NewProviderScraper(BaseScraper):
    def __init__(self, config: ScraperConfig = None):
        super().__init__(config)
        self.base_url = "https://docs.newprovider.com"
        self.provider = "newprovider"
    
    def scrape_models(self) -> List[Dict]:
        print(f"\n📄 Scraping {self.provider} models...")
        
        url = f"{self.base_url}/models"
        html = self.fetch_url(url)
        
        if not html:
            return []
        
        content = self.extract_text(html)
        code_blocks = self.extract_code_blocks(html)
        
        data = {
            'provider': self.provider,
            'content': content,
            'code_examples': code_blocks,
            'source_url': url,
            'scraped_at': datetime.now().isoformat()
        }
        
        md_path = self.save_markdown(f"{self.provider}_models_context.md",
                                     self._format_markdown(data))
        print(f"  ✅ Saved: {md_path.name}")
        
        return [data]
    
    def _format_markdown(self, data: Dict) -> str:
        # Format as markdown
        return f"# {self.provider.upper()}\n\n{data['content']}"
```

Then add to orchestrator:

```python
class ScraperOrchestrator:
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.scrapers = {
            # ... existing scrapers ...
            'newprovider': NewProviderScraper(config),
        }
```

---

## Output File Structure

```
~/aiml-scraper/
├── scraped_docs/           # Output directory
│   ├── openai_gpt-4o_context.md
│   ├── openai_gpt-4o_data.json
│   ├── anthropic_models_context.md
│   ├── anthropic_models_data.json
│   └── ... (more files)
├── cache/                  # Cache directory (for future use)
└── scraper_toolkit.py      # Main script
```

---

## File Format Examples

### Markdown Output

```markdown
# OPENAI - GPT-4O

**Source**: [https://docs.aimlapi.com/...](https://docs.aimlapi.com/...)
**Scraped**: 2025-12-11T12:00:00

## Content

[Full documentation text...]

## Code Examples

### Example 1 (python)

```python
import openai
# ... code ...
```

### Example 2 (javascript)

```javascript
const openai = require('openai');
// ... code ...
```

## Tables

### Table 1

| Parameter | Type | Description |
|-----------|------|-------------|
| model | string | Model ID |
| messages | array | Messages |
```

### JSON Output

```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "source_url": "https://docs.aimlapi.com/...",
  "scraped_at": "2025-12-11T12:00:00",
  "content": "Full text content...",
  "code_examples": [
    {
      "language": "python",
      "code": "import openai..."
    }
  ],
  "tables": [
    {
      "headers": ["Parameter", "Type"],
      "rows": [["model", "string"]]
    }
  ],
  "content_hash": "abc123..."
}
```

---

## Next Steps

After testing the scraper toolkit:

1. ✅ Test all providers
2. ✅ Verify output quality
3. ✅ Check file accessibility
4. ✅ Document any issues
5. ✅ Customize as needed
6. ✅ Integrate into web service

---

## Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Verify internet connection
3. Check file permissions
4. Review error messages carefully
5. Test with a single provider first

---

**Document Version**: 1.0
**Last Updated**: 2025-12-11
**Status**: Ready for Testing
