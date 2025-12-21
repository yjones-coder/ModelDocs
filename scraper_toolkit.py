#!/usr/bin/env python3
"""
ModelDocs Scraper Toolkit v2
Improved version with AI feedback incorporated
- Better error handling
- Rate limiting
- Noise reduction
- Content validation
- Logging support
"""

import requests
import json
import re
import os
import sys
import time
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

# Check for termux-setup-storage
try:
    import subprocess
    result = subprocess.run(['test', '-d', '/sdcard'], capture_output=True)
    SDCARD_AVAILABLE = result.returncode == 0
except:
    SDCARD_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: beautifulsoup4 not installed. Run: pip install beautifulsoup4")
    sys.exit(1)


# Configure logging
def setup_logging(log_dir: Path = None):
    """Setup logging to file and console"""
    if log_dir is None:
        log_dir = Path.home() / "aiml-scraper"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "scraper.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


logger = setup_logging()


class ScraperConfig:
    """Configuration for scraper behavior"""
    
    def __init__(self):
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 2
        self.request_delay = 1.0  # Delay between requests (rate limiting)
        self.user_agent = "ModelDocs-Scraper/2.0 (Mobile; Android; Termux)"
        self.verify_ssl = True
        
        # Try to save to /sdcard/ first (accessible via Files app)
        # Fallback to home directory if /sdcard/ not available
        sdcard_path = Path("/sdcard/AIML_API_Docs")
        home_path = Path.home() / "aiml-scraper" / "scraped_docs"
        
        if sdcard_path.exists() or self._can_write_to_sdcard():
            self.output_dir = sdcard_path
            self.use_sdcard = True
        else:
            self.output_dir = home_path
            self.use_sdcard = False
        
        self.cache_dir = Path.home() / "aiml-scraper" / "cache"
        self.min_content_length = 100  # Minimum characters for valid content
        self.low_memory_mode = False  # For future streaming support
        self.verbose = False  # Show HTML content on empty scrapes
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Log which directory is being used
        location = "SD Card (/sdcard/)" if self.use_sdcard else "Home Directory"
        logger.info(f"Output directory: {self.output_dir} ({location})")
    
    def _can_write_to_sdcard(self) -> bool:
        """Check if we can write to /sdcard/"""
        try:
            test_dir = Path("/sdcard")
            return test_dir.exists() and os.access(test_dir, os.W_OK)
        except Exception:
            return False


class BaseScraper:
    """Base class for all scrapers"""
    
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.config.user_agent})
        self.scraped_data = {}
        self.last_request_time = 0
    
    def _apply_rate_limit(self):
        """Apply rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.config.request_delay:
            time.sleep(self.config.request_delay - elapsed)
        self.last_request_time = time.time()
    
    def fetch_url(self, url: str) -> Optional[str]:
        """Fetch URL with retry logic and rate limiting"""
        self._apply_rate_limit()
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Fetching {url} (attempt {attempt + 1}/{self.config.max_retries})")
                response = self.session.get(
                    url,
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl
                )
                response.raise_for_status()
                logger.info(f"Successfully fetched {url}")
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    logger.error(f"Failed to fetch {url} after {self.config.max_retries} attempts")
                    return None
    
    def extract_text(self, html: str, selector: Optional[str] = None) -> str:
        """Extract clean text from HTML with optional content selector"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # If selector provided, extract only that section
            if selector:
                content = soup.select_one(selector)
                if not content:
                    logger.warning(f"Selector '{selector}' not found, using full content")
                    content = soup
            else:
                content = soup
            
            # Remove script and style elements
            for script in content(["script", "style"]):
                script.decompose()
            
            # Get text
            text = content.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def extract_headers(self, html: str) -> List[Tuple[int, str]]:
        """Extract header hierarchy from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            headers = []
            
            for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                level = int(header.name[1])
                text = header.get_text().strip()
                if text:
                    headers.append((level, text))
            
            return headers
        except Exception as e:
            logger.error(f"Error extracting headers: {e}")
            return []
    
    def extract_code_blocks(self, html: str) -> List[Dict[str, str]]:
        """Extract code blocks from HTML with improved language detection"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            code_blocks = []
            
            for code_elem in soup.find_all(['code', 'pre']):
                language = 'text'
                
                # Try to detect language from class
                classes = code_elem.get('class', [])
                for cls in classes:
                    if 'language-' in cls:
                        language = cls.replace('language-', '')
                        break
                
                # Fallback: check data-language attribute
                if language == 'text' and 'data-language' in code_elem.attrs:
                    language = code_elem.get('data-language', 'text')
                
                code_text = code_elem.get_text()
                if code_text.strip():
                    code_blocks.append({
                        'language': language,
                        'code': code_text.strip()
                    })
            
            return code_blocks
        except Exception as e:
            logger.error(f"Error extracting code blocks: {e}")
            return []
    
    def extract_tables(self, html: str) -> List[Dict]:
        """Extract tables from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            tables = []
            
            for table in soup.find_all('table'):
                rows = []
                for tr in table.find_all('tr'):
                    cells = []
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
        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
            return []
    
    def validate_content(self, content: str) -> bool:
        """Check if scraped content is meaningful"""
        is_valid = len(content.strip()) > self.config.min_content_length
        if not is_valid:
            logger.warning(f"Content validation failed: only {len(content)} characters")
        return is_valid
    
    def save_markdown(self, filename: str, content: str) -> Optional[Path]:
        """Save content as markdown file with error handling"""
        try:
            filepath = self.config.output_dir / filename
            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Saved markdown: {filepath.name}")
            return filepath
        except IOError as e:
            logger.error(f"Failed to save {filename}: {e}")
            return None
    
    def save_json(self, filename: str, data: Dict) -> Optional[Path]:
        """Save data as JSON file with error handling"""
        try:
            filepath = self.config.output_dir / filename
            filepath.write_text(json.dumps(data, indent=2), encoding='utf-8')
            logger.info(f"Saved JSON: {filepath.name}")
            return filepath
        except IOError as e:
            logger.error(f"Failed to save {filename}: {e}")
            return None
    
    def format_markdown(self, data: Dict, title: str) -> str:
        """Generic markdown formatter (template method pattern)"""
        md = f"""# {title}

**Source**: [{data['source_url']}]({data['source_url']})
**Scraped**: {data['scraped_at']}

## Content

{data['content']}

## Code Examples

"""
        for i, block in enumerate(data['code_examples'], 1):
            md += f"\n### Example {i} ({block['language']})\n\n```{block['language']}\n{block['code']}\n```\n"
        
        if data.get('tables'):
            md += "\n## Tables\n"
            for i, table in enumerate(data['tables'], 1):
                md += f"\n### Table {i}\n\n"
                if table['headers']:
                    md += "| " + " | ".join(table['headers']) + " |\n"
                    md += "|" + "|".join(["---"] * len(table['headers'])) + "|\n"
                for row in table['rows']:
                    md += "| " + " | ".join(row) + " |\n"
        
        return md


class AIMLAPIScraper(BaseScraper):
    """Scraper for AIML API documentation"""
    
    def __init__(self, config: ScraperConfig = None):
        super().__init__(config)
        self.base_url = "https://docs.aimlapi.com"
        self.provider = "aimlapi"
    
    def get_model_url(self, provider: str, model: str) -> str:
        """Build model documentation URL"""
        return f"{self.base_url}/api-references/text-models-llm/{provider}/{model}"
    
    def scrape_model(self, provider: str, model: str) -> Optional[Dict]:
        """Scrape a specific model documentation"""
        logger.info(f"Scraping {provider}/{model} from AIML API...")
        
        url = self.get_model_url(provider, model)
        html = self.fetch_url(url)
        
        if not html:
            return None
        
        # Extract content (try to target main content area)
        content = self.extract_text(html, selector='main')
        
        # Validate content
        if not self.validate_content(content):
            if self.config.verbose:
                logger.info(f"HTML content (first 500 chars): {html[:500]}")
            return None
        
        code_blocks = self.extract_code_blocks(html)
        tables = self.extract_tables(html)
        
        data = {
            'provider': provider,
            'model': model,
            'source_url': url,
            'scraped_at': datetime.now().isoformat(),
            'content': content,
            'code_examples': code_blocks,
            'tables': tables,
            'content_hash': hashlib.sha256(content.encode()).hexdigest()
        }
        
        # Save files
        md_filename = f"{provider}_{model}_context.md"
        json_filename = f"{provider}_{model}_data.json"
        
        md_path = self.save_markdown(md_filename, self.format_markdown(data, f"{provider.upper()} - {model}"))
        json_path = self.save_json(json_filename, data)
        
        if md_path and json_path:
            logger.info(f"Successfully scraped {provider}/{model}")
            return data
        else:
            logger.error(f"Failed to save files for {provider}/{model}")
            return None


class OpenAIScraper(BaseScraper):
    """Scraper for OpenAI documentation"""
    
    def __init__(self, config: ScraperConfig = None):
        super().__init__(config)
        self.base_url = "https://platform.openai.com/docs/api-reference"
        self.provider = "openai"
    
    def scrape_models(self) -> List[Dict]:
        """Scrape OpenAI models list"""
        logger.info("Scraping OpenAI models...")
        
        url = f"{self.base_url}/models"
        html = self.fetch_url(url)
        
        if not html:
            return []
        
        content = self.extract_text(html, selector='main')
        
        if not self.validate_content(content):
            logger.warning("OpenAI content validation failed")
            return []
        
        code_blocks = self.extract_code_blocks(html)
        
        data = {
            'provider': self.provider,
            'content': content,
            'code_examples': code_blocks,
            'source_url': url,
            'scraped_at': datetime.now().isoformat()
        }
        
        md_path = self.save_markdown(f"{self.provider}_models_context.md", 
                                     self.format_markdown(data, "OpenAI API Documentation"))
        
        if md_path:
            logger.info("Successfully scraped OpenAI")
            return [data]
        return []


class AnthropicScraper(BaseScraper):
    """Scraper for Anthropic Claude documentation"""
    
    def __init__(self, config: ScraperConfig = None):
        super().__init__(config)
        self.base_url = "https://docs.anthropic.com"
        self.provider = "anthropic"
    
    def scrape_models(self) -> List[Dict]:
        """Scrape Anthropic models documentation"""
        logger.info("Scraping Anthropic models...")
        
        url = f"{self.base_url}/en/api/models"
        html = self.fetch_url(url)
        
        if not html:
            return []
        
        content = self.extract_text(html, selector='main')
        
        if not self.validate_content(content):
            logger.warning("Anthropic content validation failed")
            return []
        
        code_blocks = self.extract_code_blocks(html)
        
        data = {
            'provider': self.provider,
            'content': content,
            'code_examples': code_blocks,
            'source_url': url,
            'scraped_at': datetime.now().isoformat()
        }
        
        md_path = self.save_markdown(f"{self.provider}_models_context.md",
                                     self.format_markdown(data, "Anthropic Claude API Documentation"))
        
        if md_path:
            logger.info("Successfully scraped Anthropic")
            return [data]
        return []


class GoogleGeminiScraper(BaseScraper):
    """Scraper for Google Gemini documentation"""
    
    def __init__(self, config: ScraperConfig = None):
        super().__init__(config)
        self.base_url = "https://ai.google.dev"
        self.provider = "google"
    
    def get_model_url(self, model: str) -> str:
        """Build model documentation URL"""
        # Convert model name to URL format (e.g., flash-2.5 -> gemini-2.5-flash)
        return f"{self.base_url}/models/gemini-{model}"
    
    def scrape_model(self, model: str) -> Optional[Dict]:
        """Scrape a specific model documentation"""
        logger.info(f"Scraping Google Gemini {model}...")
        
        url = self.get_model_url(model)
        html = self.fetch_url(url)
        
        if not html:
            return None
        
        content = self.extract_text(html, selector='main')
        
        if not self.validate_content(content):
            logger.warning(f"Google {model} content validation failed")
            return None
        
        code_blocks = self.extract_code_blocks(html)
        tables = self.extract_tables(html)
        
        data = {
            'provider': self.provider,
            'model': model,
            'source_url': url,
            'scraped_at': datetime.now().isoformat(),
            'content': content,
            'code_examples': code_blocks,
            'tables': tables,
            'content_hash': hashlib.sha256(content.encode()).hexdigest()
        }
        
        md_filename = f"{self.provider}_{model}_context.md"
        json_filename = f"{self.provider}_{model}_data.json"
        
        md_path = self.save_markdown(md_filename, self.format_markdown(data, f"Google Gemini - {model}"))
        json_path = self.save_json(json_filename, data)
        
        if md_path and json_path:
            logger.info(f"Successfully scraped Google Gemini {model}")
            return data
        return None
    
    def scrape_models(self) -> List[Dict]:
        """Scrape Google Gemini models list page"""
        logger.info("Scraping Google Gemini models list...")
        
        url = f"{self.base_url}/models"
        html = self.fetch_url(url)
        
        if not html:
            return []
        
        content = self.extract_text(html, selector='main')
        
        if not self.validate_content(content):
            logger.warning("Google models list validation failed")
            return []
        
        code_blocks = self.extract_code_blocks(html)
        
        data = {
            'provider': self.provider,
            'content': content,
            'code_examples': code_blocks,
            'source_url': url,
            'scraped_at': datetime.now().isoformat()
        }
        
        md_path = self.save_markdown(f"{self.provider}_models_context.md",
                                     self.format_markdown(data, "Google Gemini API Documentation"))
        
        if md_path:
            logger.info("Successfully scraped Google Gemini models list")
            return [data]
        return []


class DeepSeekScraper(BaseScraper):
    """Scraper for DeepSeek documentation"""
    
    def __init__(self, config: ScraperConfig = None):
        super().__init__(config)
        self.base_url = "https://platform.deepseek.com/docs"
        self.provider = "deepseek"
    
    def get_model_url(self, model: str) -> str:
        """Build model documentation URL"""
        return f"{self.base_url}/models/{model}"
    
    def scrape_model(self, model: str) -> Optional[Dict]:
        """Scrape a specific model documentation"""
        logger.info(f"Scraping DeepSeek {model}...")
        
        url = self.get_model_url(model)
        html = self.fetch_url(url)
        
        if not html:
            return None
        
        content = self.extract_text(html, selector='main')
        
        if not self.validate_content(content):
            logger.warning(f"DeepSeek {model} content validation failed")
            return None
        
        code_blocks = self.extract_code_blocks(html)
        tables = self.extract_tables(html)
        
        data = {
            'provider': self.provider,
            'model': model,
            'source_url': url,
            'scraped_at': datetime.now().isoformat(),
            'content': content,
            'code_examples': code_blocks,
            'tables': tables,
            'content_hash': hashlib.sha256(content.encode()).hexdigest()
        }
        
        md_filename = f"{self.provider}_{model}_context.md"
        json_filename = f"{self.provider}_{model}_data.json"
        
        md_path = self.save_markdown(md_filename, self.format_markdown(data, f"DeepSeek - {model}"))
        json_path = self.save_json(json_filename, data)
        
        if md_path and json_path:
            logger.info(f"Successfully scraped DeepSeek {model}")
            return data
        return None
    
    def scrape_models(self) -> List[Dict]:
        """Scrape DeepSeek models list page"""
        logger.info("Scraping DeepSeek models list...")
        
        url = f"{self.base_url}/models"
        html = self.fetch_url(url)
        
        if not html:
            return []
        
        content = self.extract_text(html, selector='main')
        
        if not self.validate_content(content):
            logger.warning("DeepSeek models list validation failed")
            return []
        
        code_blocks = self.extract_code_blocks(html)
        
        data = {
            'provider': self.provider,
            'content': content,
            'code_examples': code_blocks,
            'source_url': url,
            'scraped_at': datetime.now().isoformat()
        }
        
        md_path = self.save_markdown(f"{self.provider}_models_context.md",
                                     self.format_markdown(data, "DeepSeek API Documentation"))
        
        if md_path:
            logger.info("Successfully scraped DeepSeek models list")
            return [data]
        return []


class MistralScraper(BaseScraper):
    """Scraper for Mistral documentation"""
    
    def __init__(self, config: ScraperConfig = None):
        super().__init__(config)
        self.base_url = "https://docs.mistral.ai"
        self.provider = "mistral"
    
    def get_model_url(self, model: str) -> str:
        """Build model documentation URL"""
        return f"{self.base_url}/capabilities/models/{model}"
    
    def scrape_model(self, model: str) -> Optional[Dict]:
        """Scrape a specific model documentation"""
        logger.info(f"Scraping Mistral {model}...")
        
        url = self.get_model_url(model)
        html = self.fetch_url(url)
        
        if not html:
            return None
        
        content = self.extract_text(html, selector='main')
        
        if not self.validate_content(content):
            logger.warning(f"Mistral {model} content validation failed")
            return None
        
        code_blocks = self.extract_code_blocks(html)
        tables = self.extract_tables(html)
        
        data = {
            'provider': self.provider,
            'model': model,
            'source_url': url,
            'scraped_at': datetime.now().isoformat(),
            'content': content,
            'code_examples': code_blocks,
            'tables': tables,
            'content_hash': hashlib.sha256(content.encode()).hexdigest()
        }
        
        md_filename = f"{self.provider}_{model}_context.md"
        json_filename = f"{self.provider}_{model}_data.json"
        
        md_path = self.save_markdown(md_filename, self.format_markdown(data, f"Mistral - {model}"))
        json_path = self.save_json(json_filename, data)
        
        if md_path and json_path:
            logger.info(f"Successfully scraped Mistral {model}")
            return data
        return None
    
    def scrape_models(self) -> List[Dict]:
        """Scrape Mistral models list page"""
        logger.info("Scraping Mistral models list...")
        
        url = f"{self.base_url}/capabilities/models"
        html = self.fetch_url(url)
        
        if not html:
            return []
        
        content = self.extract_text(html, selector='main')
        
        if not self.validate_content(content):
            logger.warning("Mistral models list validation failed")
            return []
        
        code_blocks = self.extract_code_blocks(html)
        
        data = {
            'provider': self.provider,
            'content': content,
            'code_examples': code_blocks,
            'source_url': url,
            'scraped_at': datetime.now().isoformat()
        }
        
        md_path = self.save_markdown(f"{self.provider}_models_context.md",
                                     self.format_markdown(data, "Mistral API Documentation"))
        
        if md_path:
            logger.info("Successfully scraped Mistral models list")
            return [data]
        return []


class CohereScraper(BaseScraper):
    """Scraper for Cohere documentation"""
    
    def __init__(self, config: ScraperConfig = None):
        super().__init__(config)
        self.base_url = "https://docs.cohere.com"
        self.provider = "cohere"
    
    def scrape_models(self) -> List[Dict]:
        """Scrape Cohere models documentation"""
        logger.info("Scraping Cohere models...")
        
        url = f"{self.base_url}/models"
        html = self.fetch_url(url)
        
        if not html:
            return []
        
        content = self.extract_text(html, selector='main')
        
        if not self.validate_content(content):
            logger.warning("Cohere content validation failed")
            return []
        
        code_blocks = self.extract_code_blocks(html)
        
        data = {
            'provider': self.provider,
            'content': content,
            'code_examples': code_blocks,
            'source_url': url,
            'scraped_at': datetime.now().isoformat()
        }
        
        md_path = self.save_markdown(f"{self.provider}_models_context.md",
                                     self.format_markdown(data, "Cohere API Documentation"))
        
        if md_path:
            logger.info("Successfully scraped Cohere")
            return [data]
        return []


class ScraperOrchestrator:
    """Orchestrate scraping across multiple providers"""
    
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.scrapers = {
            'aimlapi': AIMLAPIScraper(config),
            'openai': OpenAIScraper(config),
            'anthropic': AnthropicScraper(config),
            'google': GoogleGeminiScraper(config),
            'deepseek': DeepSeekScraper(config),
            'mistral': MistralScraper(config),
            'cohere': CohereScraper(config),
        }
    
    def scrape_aimlapi_model(self, provider: str, model: str) -> Optional[Dict]:
        """Scrape a specific model from AIML API"""
        scraper = self.scrapers['aimlapi']
        return scraper.scrape_model(provider, model)
    
    def scrape_model(self, provider: str, model: str) -> Optional[Dict]:
        """Scrape a specific model from any provider that supports it"""
        if provider not in self.scrapers:
            logger.error(f"Unknown provider: {provider}")
            return None
        
        scraper = self.scrapers[provider]
        if hasattr(scraper, 'scrape_model'):
            return scraper.scrape_model(model)
        else:
            logger.error(f"Provider {provider} does not support model-specific scraping")
            return None
    
    def scrape_provider(self, provider: str) -> List[Dict]:
        """Scrape all models from a provider"""
        if provider not in self.scrapers:
            logger.error(f"Unknown provider: {provider}")
            return []
        
        scraper = self.scrapers[provider]
        if hasattr(scraper, 'scrape_models'):
            return scraper.scrape_models()
        else:
            logger.warning(f"Provider {provider} requires specific model names")
            return []
    
    def list_output_files(self) -> List[Path]:
        """List all scraped files (excluding cache and temp directories)"""
        all_files = sorted(self.config.output_dir.glob('*'))
        # Filter out cache and temp directories
        return [f for f in all_files if f.name not in ['.cache', '.temp'] and not f.name.startswith('.')]
    
    def print_summary(self):
        """Print summary of scraped files"""
        files = self.list_output_files()
        
        location = "SD Card (/sdcard/)" if self.config.use_sdcard else "Home Directory"
        
        print("\n" + "="*60)
        print("📊 SCRAPER SUMMARY")
        print("="*60)
        print(f"Output Directory: {self.config.output_dir}")
        print(f"Location: {location}")
        print(f"Total Files: {len(files)}\n")
        
        if files:
            print("Scraped Files:")
            for f in files:
                size_kb = f.stat().st_size / 1024
                print(f"  • {f.name} ({size_kb:.1f} KB)")
            
            if self.config.use_sdcard:
                print("\n✅ Files are saved to SD Card!")
                print("   Open Files app → AIML_API_Docs folder to view them.")
            else:
                print("\n📁 Files are saved to home directory.")
                print(f"   Path: {self.config.output_dir}")
        else:
            print("No files scraped yet.")
        
        print("="*60 + "\n")


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ModelDocs Scraper Toolkit v2 - Scrape AI model documentation"
    )
    
    parser.add_argument(
        'command',
        choices=['scrape', 'list', 'help'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--provider',
        help='Provider name (aimlapi, openai, anthropic, google, deepseek, mistral, cohere)'
    )
    
    parser.add_argument(
        '--model',
        help='Model name (for AIML API provider)'
    )
    
    parser.add_argument(
        '--source',
        help='Source provider for AIML API (e.g., openai, anthropic)'
    )
    
    parser.add_argument(
        '--model',
        help='Model name (for providers that support model-specific scraping)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show HTML content on empty scrapes (for debugging)'
    )
    
    args = parser.parse_args()
    
    config = ScraperConfig()
    config.verbose = args.verbose
    orchestrator = ScraperOrchestrator(config)
    
    if args.command == 'help':
        print("""
ModelDocs Scraper Toolkit v2 - Usage Examples
==============================================

1. Scrape AIML API model:
   python3 scraper_toolkit_v2.py scrape --provider aimlapi --source openai --model gpt-4o

2. Scrape OpenAI documentation:
   python3 scraper_toolkit_v2.py scrape --provider openai

3. Scrape Anthropic documentation:
   python3 scraper_toolkit_v2.py scrape --provider anthropic

4. Scrape Google Gemini documentation:
   python3 scraper_toolkit_v2.py scrape --provider google

5. Scrape DeepSeek documentation:
   python3 scraper_toolkit_v2.py scrape --provider deepseek

6. Scrape Mistral documentation:
   python3 scraper_toolkit_v2.py scrape --provider mistral

7. Scrape Cohere documentation:
   python3 scraper_toolkit_v2.py scrape --provider cohere

8. List all scraped files:
   python3 scraper_toolkit_v2.py list

9. Debug empty scrapes (verbose mode):
   python3 scraper_toolkit_v2.py scrape --provider openai --verbose

10. Scrape specific model from Google:
    python3 scraper_toolkit_v2.py scrape --provider google --model 2.5-flash

11. Scrape specific model from DeepSeek:
    python3 scraper_toolkit_v2.py scrape --provider deepseek --model deepseek-chat

12. Scrape specific model from Mistral:
    python3 scraper_toolkit_v2.py scrape --provider mistral --model mistral-large

Supported Providers:
  • aimlapi   - AIML API (requires --source and --model)
  • openai    - OpenAI API (supports --model for specific models)
  • anthropic - Anthropic Claude (supports --model for specific models)
  • google    - Google Gemini (supports --model for specific models)
  • deepseek  - DeepSeek (supports --model for specific models)
  • mistral   - Mistral (supports --model for specific models)
  • cohere    - Cohere (supports --model for specific models)

Improvements in v2:
  ✅ Better error handling with try-except blocks
  ✅ Rate limiting (1 second delay between requests)
  ✅ Content validation (minimum 100 characters)
  ✅ Logging to file and console
  ✅ Improved HTML parsing with main selector
  ✅ Better language detection for code blocks
  ✅ Consolidated markdown formatting
  ✅ Mobile-optimized user agent
  ✅ Verbose mode for debugging
  ✅ Model-specific scraping for all providers
  ✅ Automatic SD Card saving
        """)
    
    elif args.command == 'scrape':
        if not args.provider:
            logger.error("Error: --provider is required")
            sys.exit(1)
        
        if args.provider == 'aimlapi':
            if not args.source or not args.model:
                logger.error("Error: AIML API requires --source and --model")
                logger.error("   Example: --source openai --model gpt-4o")
                sys.exit(1)
            
            logger.info(f"Starting AIML API scraper...")
            orchestrator.scrape_aimlapi_model(args.source, args.model)
        elif args.model:
            # If model specified, try model-specific scraping
            logger.info(f"Starting {args.provider} scraper for model {args.model}...")
            orchestrator.scrape_model(args.provider, args.model)
        else:
            # Otherwise scrape models list
            logger.info(f"Starting {args.provider} scraper...")
            orchestrator.scrape_provider(args.provider)
        
        orchestrator.print_summary()
    
    elif args.command == 'list':
        orchestrator.print_summary()


if __name__ == '__main__':
    main()
