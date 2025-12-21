# Scraper Technical Deep Dive

## How Your Current Scraper Works

---

# PART 1: ARCHITECTURE OVERVIEW

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Pixel 9a (Termux)                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         scraper_toolkit_v2.py (Main Script)          │   │
│  │                                                       │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  ScraperConfig                                 │  │   │
│  │  │  - Timeout: 30s                               │  │   │
│  │  │  - Retries: 3                                 │  │   │
│  │  │  - Rate limit: 1 sec between requests         │  │   │
│  │  │  - Output: /sdcard/AIML_API_Docs/             │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                         ▼                             │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  ScraperOrchestrator                           │  │   │
│  │  │  - Manages all provider scrapers              │  │   │
│  │  │  - Routes requests to correct scraper         │  │   │
│  │  │  - Prints summary                             │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                         ▼                             │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  Provider Scrapers                             │  │   │
│  │  │  - AIMLAPIScraper                             │  │   │
│  │  │  - OpenAIScraper                              │  │   │
│  │  │  - AnthropicScraper                           │  │   │
│  │  │  - GoogleGeminiScraper                        │  │   │
│  │  │  - DeepSeekScraper                            │  │   │
│  │  │  - MistralScraper                             │  │   │
│  │  │  - CohereScraper                              │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                         ▼                             │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  BaseScraper (Core Logic)                      │  │   │
│  │  │  - fetch_url() - Get HTML                      │  │   │
│  │  │  - extract_text() - Parse content             │  │   │
│  │  │  - extract_code_blocks() - Get code           │  │   │
│  │  │  - extract_tables() - Get tables              │  │   │
│  │  │  - validate_content() - Check quality        │  │   │
│  │  │  - save_markdown() - Save .md files           │  │   │
│  │  │  - save_json() - Save .json files             │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                         ▼                             │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  External Libraries                            │  │   │
│  │  │  - requests (HTTP requests)                   │  │   │
│  │  │  - BeautifulSoup (HTML parsing)               │  │   │
│  │  │  - pathlib (File operations)                  │  │   │
│  │  │  - logging (Debug output)                     │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              ▼
                    ┌──────────────────┐
                    │  Internet (HTTP) │
                    │  Documentation   │
                    │  Websites        │
                    └──────────────────┘
                              ▼
                    ┌──────────────────┐
                    │  /sdcard/        │
                    │  AIML_API_Docs/  │
                    │  (Output files)  │
                    └──────────────────┘
```

---

# PART 2: EXECUTION FLOW

## Step-by-Step Workflow

### Step 1: User Runs Command
```bash
python3 scraper_toolkit_v2.py scrape --provider google --model 2.5-flash
```

### Step 2: CLI Parsing
```python
# main() function processes arguments
args.command = 'scrape'
args.provider = 'google'
args.model = '2.5-flash'
```

### Step 3: Configuration Setup
```python
config = ScraperConfig()
# Checks if /sdcard/ is writable
# Sets output_dir = /sdcard/AIML_API_Docs
# Initializes logging to ~/aiml-scraper/scraper.log
```

### Step 4: Orchestrator Initialization
```python
orchestrator = ScraperOrchestrator(config)
# Creates instances of all 7 provider scrapers
# Each scraper inherits from BaseScraper
```

### Step 5: Route to Correct Scraper
```python
if args.model:
    # Model-specific scraping
    orchestrator.scrape_model(args.provider, args.model)
else:
    # Models list scraping
    orchestrator.scrape_provider(args.provider)
```

### Step 6: Execute Scraper
```python
# For Google with model '2.5-flash':
scraper = orchestrator.scrapers['google']  # GoogleGeminiScraper instance
scraper.scrape_model('2.5-flash')
```

---

# PART 3: DETAILED SCRAPING PROCESS

## What Happens Inside scrape_model()

### Phase 1: URL Construction
```python
def scrape_model(self, model: str) -> Optional[Dict]:
    # Build the URL
    url = self.get_model_url(model)
    # For Google: https://ai.google.dev/models/gemini-2.5-flash
    
    logger.info(f"Scraping Google Gemini {model}...")
```

### Phase 2: Fetch HTML
```python
def fetch_url(self, url: str) -> Optional[str]:
    # Apply rate limiting (1 second delay)
    self._apply_rate_limit()
    
    # Try up to 3 times with exponential backoff
    for attempt in range(3):
        try:
            # Make HTTP GET request
            response = self.session.get(
                url,
                timeout=30,  # 30 second timeout
                verify=True  # SSL verification enabled
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Return HTML content
            return response.text
            
        except RequestException as e:
            # Log error and retry
            if attempt < 2:
                time.sleep(2)  # Wait 2 seconds before retry
            else:
                logger.error(f"Failed after 3 attempts")
                return None
```

**What's happening**:
- ✅ Sends HTTP GET request to the URL
- ✅ Waits 1 second (rate limiting)
- ✅ Retries up to 3 times if it fails
- ✅ Returns raw HTML as string

### Phase 3: Extract Content
```python
def scrape_model(self, model: str) -> Optional[Dict]:
    html = self.fetch_url(url)
    
    # Extract main content (reduce noise)
    content = self.extract_text(html, selector='main')
```

**What extract_text() does**:
```python
def extract_text(self, html: str, selector: Optional[str] = None) -> str:
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # If selector provided, target specific element
    if selector:
        content = soup.select_one(selector)  # Find <main> element
    else:
        content = soup  # Use entire page
    
    # Remove script and style tags (noise)
    for script in content(["script", "style"]):
        script.decompose()
    
    # Get all text
    text = content.get_text()
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text
```

**What's happening**:
- ✅ Parses HTML into a tree structure
- ✅ Finds `<main>` element (article content)
- ✅ Removes `<script>` and `<style>` tags
- ✅ Extracts all text
- ✅ Cleans up extra whitespace
- ✅ Returns clean text

### Phase 4: Validate Content
```python
def scrape_model(self, model: str) -> Optional[Dict]:
    # Check if content is meaningful
    if not self.validate_content(content):
        logger.warning(f"Content validation failed")
        return None
```

**What validate_content() does**:
```python
def validate_content(self, content: str) -> bool:
    # Ensure minimum 100 characters
    is_valid = len(content.strip()) > 100
    
    if not is_valid:
        logger.warning(f"Only {len(content)} characters")
    
    return is_valid
```

**What's happening**:
- ✅ Checks if content has at least 100 characters
- ✅ Rejects empty or minimal content
- ✅ Logs warning if validation fails

### Phase 5: Extract Code Blocks
```python
def scrape_model(self, model: str) -> Optional[Dict]:
    code_blocks = self.extract_code_blocks(html)
```

**What extract_code_blocks() does**:
```python
def extract_code_blocks(self, html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, 'html.parser')
    code_blocks = []
    
    # Find all <code> and <pre> elements
    for code_elem in soup.find_all(['code', 'pre']):
        language = 'text'  # Default language
        
        # Try to detect language from class
        classes = code_elem.get('class', [])
        for cls in classes:
            if 'language-' in cls:
                language = cls.replace('language-', '')
                break
        
        # Fallback: check data-language attribute
        if language == 'text' and 'data-language' in code_elem.attrs:
            language = code_elem.get('data-language', 'text')
        
        # Extract code text
        code_text = code_elem.get_text()
        if code_text.strip():
            code_blocks.append({
                'language': language,
                'code': code_text.strip()
            })
    
    return code_blocks
```

**What's happening**:
- ✅ Finds all `<code>` and `<pre>` tags
- ✅ Detects programming language from HTML class
- ✅ Falls back to data-language attribute
- ✅ Extracts code content
- ✅ Returns list of code blocks with language

### Phase 6: Extract Tables
```python
def scrape_model(self, model: str) -> Optional[Dict]:
    tables = self.extract_tables(html)
```

**What extract_tables() does**:
```python
def extract_tables(self, html: str) -> List[Dict]:
    soup = BeautifulSoup(html, 'html.parser')
    tables = []
    
    # Find all <table> elements
    for table in soup.find_all('table'):
        rows = []
        
        # Extract each row
        for tr in table.find_all('tr'):
            cells = []
            
            # Extract each cell
            for td in tr.find_all(['td', 'th']):
                cells.append(td.get_text().strip())
            
            if cells:
                rows.append(cells)
        
        if rows:
            tables.append({
                'headers': rows[0] if rows else [],
                'rows': rows[1:] if len(rows) > 1 else []
            })
    
    return tables
```

**What's happening**:
- ✅ Finds all `<table>` elements
- ✅ Extracts rows and cells
- ✅ Separates headers from data
- ✅ Returns structured table data

### Phase 7: Create Data Dictionary
```python
def scrape_model(self, model: str) -> Optional[Dict]:
    data = {
        'provider': 'google',
        'model': '2.5-flash',
        'source_url': 'https://ai.google.dev/models/gemini-2.5-flash',
        'scraped_at': '2025-12-11T16:55:51.602',
        'content': '...',  # Full text content
        'code_examples': [
            {'language': 'python', 'code': '...'},
            {'language': 'javascript', 'code': '...'}
        ],
        'tables': [
            {'headers': [...], 'rows': [...]}
        ],
        'content_hash': 'abc123...'  # SHA256 hash
    }
```

### Phase 8: Format as Markdown
```python
def scrape_model(self, model: str) -> Optional[Dict]:
    md_content = self.format_markdown(data, f"Google Gemini - {model}")
```

**What format_markdown() produces**:
```markdown
# Google Gemini - 2.5-flash

**Source**: [https://ai.google.dev/models/gemini-2.5-flash](...)
**Scraped**: 2025-12-11T16:55:51.602

## Content

[Full text content here...]

## Code Examples

### Example 1 (python)

```python
[Code here]
```

### Example 2 (javascript)

```javascript
[Code here]
```

## Tables

### Table 1

| Header 1 | Header 2 |
|----------|----------|
| Data 1   | Data 2   |
```

### Phase 9: Save Files
```python
def scrape_model(self, model: str) -> Optional[Dict]:
    # Save markdown file
    md_path = self.save_markdown(
        f"google_2.5-flash_context.md",
        md_content
    )
    
    # Save JSON file
    json_path = self.save_json(
        f"google_2.5-flash_data.json",
        data
    )
```

**What save_markdown() does**:
```python
def save_markdown(self, filename: str, content: str) -> Optional[Path]:
    try:
        filepath = self.config.output_dir / filename
        # /sdcard/AIML_API_Docs/google_2.5-flash_context.md
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Saved markdown: {filepath.name}")
        return filepath
    except IOError as e:
        logger.error(f"Failed to save {filename}: {e}")
        return None
```

**What's happening**:
- ✅ Creates full file path
- ✅ Writes content to file
- ✅ Logs success or error
- ✅ Returns file path

### Phase 10: Print Summary
```python
orchestrator.print_summary()
```

**Output**:
```
============================================================
📊 SCRAPER SUMMARY
============================================================
Output Directory: /sdcard/AIML_API_Docs
Location: SD Card (/sdcard/)
Total Files: 2

Scraped Files:
  • google_2.5-flash_context.md (25.3 KB)
  • google_2.5-flash_data.json (23.1 KB)

✅ Files are saved to SD Card!
   Open Files app → AIML_API_Docs folder to view them.
============================================================
```

---

# PART 4: DATA FLOW DIAGRAM

```
Command Line Input
        ↓
┌──────────────────────┐
│  Parse Arguments     │
│  - provider: google  │
│  - model: 2.5-flash  │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Create Config       │
│  - timeout: 30s      │
│  - retries: 3        │
│  - output: /sdcard/  │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Create Orchestrator │
│  - Initialize all    │
│    7 scrapers        │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Route to Scraper    │
│  GoogleGeminiScraper │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Build URL           │
│  https://ai.google.. │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Fetch HTML (HTTP)   │
│  - Rate limit (1s)   │
│  - Retry (3x)        │
│  - Timeout (30s)     │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Parse HTML          │
│  BeautifulSoup       │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Extract Content     │
│  - Text              │
│  - Code blocks       │
│  - Tables            │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Validate Content    │
│  - Min 100 chars     │
│  - Not empty         │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Create Data Dict    │
│  - provider          │
│  - model             │
│  - content           │
│  - code_examples     │
│  - tables            │
│  - hash              │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Format Markdown     │
│  - Headers           │
│  - Content           │
│  - Code blocks       │
│  - Tables            │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Save Files          │
│  - .md file          │
│  - .json file        │
│  - /sdcard/          │
└──────────────────────┘
        ↓
┌──────────────────────┐
│  Print Summary       │
│  - File count        │
│  - File sizes        │
│  - Location          │
└──────────────────────┘
        ↓
    Files Ready!
```

---

# PART 5: KEY CONCEPTS

## 1. Rate Limiting
```python
def _apply_rate_limit(self):
    elapsed = time.time() - self.last_request_time
    if elapsed < self.config.request_delay:
        time.sleep(self.config.request_delay - elapsed)
    self.last_request_time = time.time()
```

**Why**: Prevents overwhelming servers, avoids IP bans

## 2. Retry Logic
```python
for attempt in range(self.config.max_retries):
    try:
        response = self.session.get(url, timeout=30)
        return response.text
    except RequestException:
        if attempt < 2:
            time.sleep(2)
```

**Why**: Handles temporary network failures, improves reliability

## 3. Content Validation
```python
if not self.validate_content(content):
    return None
```

**Why**: Ensures we only save meaningful content, avoids empty files

## 4. Selector-Based Extraction
```python
content = self.extract_text(html, selector='main')
```

**Why**: Targets article content, reduces navigation noise

## 5. Content Hashing
```python
'content_hash': hashlib.sha256(content.encode()).hexdigest()
```

**Why**: Detects duplicate content, tracks changes over time

---

# PART 6: LIMITATIONS & HOW THEY WORK

## Limitation 1: Static HTML Only
**What it means**: Can't scrape JavaScript-rendered content

**Why**: `requests` library gets raw HTML before JavaScript runs

**Example**:
```html
<!-- What requests sees: -->
<div id="app"></div>
<script>
  // This code hasn't run yet
  document.getElementById('app').innerHTML = 'Content here';
</script>

<!-- What browser sees: -->
<div id="app">Content here</div>
```

**Impact**: Can't scrape modern SPAs (Google, DeepSeek, Mistral)

## Limitation 2: Navigation Noise
**What it means**: Gets headers, footers, sidebars

**Why**: Without JavaScript, can't identify main content

**Solution**: Use `selector='main'` to target article body

## Limitation 3: Rate Limiting
**What it means**: Can't scrape too fast

**Why**: Servers block rapid requests

**Solution**: 1-second delay between requests

## Limitation 4: IP Blocking
**What it means**: Server may block your IP

**Why**: Looks like bot activity

**Solution**: Firecrawl uses rotating proxies

---

# PART 7: PERFORMANCE METRICS

## Typical Scraping Times

```
URL Fetch:           2-5 seconds
HTML Parsing:        0.1-0.5 seconds
Content Extraction:  0.1-0.2 seconds
Validation:          0.01 seconds
Markdown Formatting: 0.05 seconds
File Writing:        0.1-0.2 seconds
─────────────────────────────
Total per scrape:    2.5-6.5 seconds
```

## Memory Usage

```
Script startup:      ~30 MB
Per scrape:          ~5-10 MB
Peak (large page):   ~50 MB
```

## Network Usage

```
Per scrape:          100 KB - 2 MB
Typical:             500 KB
Large pages:         5-10 MB
```

---

# PART 8: ERROR HANDLING

## What Happens If...

### Network Error
```
Attempt 1: Fails → Wait 2s
Attempt 2: Fails → Wait 2s
Attempt 3: Fails → Log error, return None
```

### Empty Content
```
Content length: 50 characters
Validation: Failed (< 100 chars)
Result: Return None, log warning
```

### File Write Error
```
try:
    filepath.write_text(content)
except IOError as e:
    logger.error(f"Failed to save: {e}")
    return None
```

### Invalid HTML
```
BeautifulSoup handles malformed HTML gracefully
- Missing tags: Still parses
- Broken nesting: Auto-corrects
- Invalid encoding: Handles with fallback
```

---

# SUMMARY

Your scraper works by:

1. **Fetching** raw HTML from documentation websites
2. **Parsing** HTML into a structured format
3. **Extracting** text, code, and tables
4. **Validating** that content is meaningful
5. **Formatting** as Markdown and JSON
6. **Saving** to `/sdcard/AIML_API_Docs/`
7. **Logging** all operations for debugging

**Strengths**:
- ✅ Simple and reliable
- ✅ Works offline (no API needed)
- ✅ Fast (2-6 seconds per scrape)
- ✅ Low memory usage
- ✅ Good error handling

**Weaknesses**:
- ❌ Can't handle JavaScript
- ❌ Gets navigation noise
- ❌ Can be rate limited
- ❌ May get IP blocked

---

**Document Version**: 1.0
**Last Updated**: 2025-12-11
**Status**: Complete
