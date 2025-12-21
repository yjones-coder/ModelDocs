# AIML API Documentation Scraper - Mobile Setup Guide

## For Pixel 9a with Termux

This guide will help you set up the AIML API scraper on your Android phone so that generated documentation files appear in your phone's native **Files app**.

---

## Prerequisites

- **Termux** app installed from F-Droid or Google Play
- **Internet connection**
- **Storage permission** (we'll set this up)

---

## Step 1: Install Termux

If you haven't already:
1. Open Google Play Store or F-Droid
2. Search for "Termux"
3. Install the app
4. Open Termux

---

## Step 2: Grant Storage Permission

This is crucial! Termux needs permission to write to your phone's shared storage.

In Termux, run:
```bash
termux-setup-storage
```

This will:
- Ask for permission to access files
- Create a `storage` folder in Termux home
- Link to your phone's `/sdcard/` directory

**Tap "Allow" when prompted!**

---

## Step 3: Install Dependencies

```bash
# Update package manager
pkg update && pkg upgrade -y

# Install required tools
pkg install -y curl jq python3

# Install Python packages
pip install requests beautifulsoup4
```

This takes a few minutes. Let it finish.

---

## Step 4: Download the Scripts

### Option A: Using curl (Easiest)

```bash
# Create a working directory
mkdir -p ~/aiml-scraper
cd ~/aiml-scraper

# Download the mobile-optimized bash script
curl -o aiml_scraper_mobile.sh https://your-url-here/aiml_scraper_mobile.sh

# Download the mobile-optimized Python script
curl -o aiml_advanced_scraper_mobile.py https://your-url-here/aiml_advanced_scraper_mobile.py

# Make them executable
chmod +x aiml_scraper_mobile.sh
chmod +x aiml_advanced_scraper_mobile.py
```

### Option B: Manual Transfer

1. Transfer the files to your phone via:
   - Email attachment
   - Cloud storage (Google Drive, OneDrive, etc.)
   - USB cable and file manager
   - AirDrop (if using iPhone to transfer)

2. Move them to Termux:
   ```bash
   mkdir -p ~/aiml-scraper
   cd ~/aiml-scraper
   # Files should be in ~/storage/downloads/ or similar
   ```

---

## Step 5: Verify Setup

Check that everything is working:

```bash
cd ~/aiml-scraper

# List files
ls -la

# Check if /sdcard/ is accessible
ls -la /sdcard/

# You should see your phone's storage folders
```

---

## Step 6: Generate Your First Documentation

```bash
# Generate context for gpt-4o
./aiml_scraper_mobile.sh gpt-4o

# Or use Python version
python3 aiml_advanced_scraper_mobile.py gpt-4o
```

The script will:
1. Check dependencies ✓
2. Set up storage ✓
3. Fetch documentation from AIML API
4. Generate `gpt-4o_context.md`
5. Save to `/sdcard/AIML_API_Docs/`

---

## Step 7: Access Files on Your Phone

Now the magic part! The generated files are accessible through your phone's native Files app:

1. **Open Files app** on your phone
2. **Navigate to**: Internal Storage → AIML_API_Docs
3. **You'll see**: `gpt-4o_context.md` (or whatever model you scraped)
4. **Open the file** with any text editor or share it

---

## Usage Examples

### Generate Documentation for Different Models

```bash
cd ~/aiml-scraper

# OpenAI models
./aiml_scraper_mobile.sh gpt-4o
./aiml_scraper_mobile.sh gpt-4o-mini
./aiml_scraper_mobile.sh o1

# Anthropic models
./aiml_scraper_mobile.sh claude-3-sonnet
./aiml_scraper_mobile.sh claude-3-opus

# DeepSeek models
./aiml_scraper_mobile.sh deepseek-chat

# Google models
./aiml_scraper_mobile.sh gemini-2.0-flash

# Using Python scraper
python3 aiml_advanced_scraper_mobile.py gpt-4o
python3 aiml_advanced_scraper_mobile.py claude-3-sonnet
```

---

## File Locations

### In Termux:
```
~/aiml-scraper/                    # Working directory
/sdcard/AIML_API_Docs/            # Generated files (accessible in Files app)
/sdcard/AIML_API_Docs/.cache/     # Cached HTML (hidden)
/sdcard/AIML_API_Docs/.temp/      # Temporary files (hidden)
```

### In Files App:
```
Internal Storage
└── AIML_API_Docs
    ├── gpt-4o_context.md
    ├── claude-3-sonnet_context.md
    ├── deepseek-chat_context.md
    └── ...
```

---

## Sharing Generated Files

Once you have the context.md file in your Files app:

### Share with AI Assistant:

1. **Open the file** in Files app
2. **Tap "Share"** or **"Open with"**
3. **Choose your AI app** (Claude, ChatGPT, etc.)
4. **Paste the content** into your AI chat
5. **Ask for help** building scripts/pipelines

### Example Prompt:

```
I have AIML API documentation context for gpt-4o.

[Paste context.md here]

Can you help me:
1. Build a script that calls this API
2. Implement error handling and retries
3. Add streaming support
4. Optimize for cost
```

---

## Troubleshooting

### "Permission denied" when running script

**Solution**: Make sure file is executable
```bash
chmod +x aiml_scraper_mobile.sh
chmod +x aiml_advanced_scraper_mobile.py
```

### "curl: command not found"

**Solution**: Install curl
```bash
pkg install -y curl
```

### "Failed to fetch" errors

**Solutions**:
- Check internet connection: `ping google.com`
- Try again (servers might be busy)
- Clear cache: `rm -rf /sdcard/AIML_API_Docs/.cache`

### Files not appearing in Files app

**Solutions**:
1. Check file was created: `ls -la /sdcard/AIML_API_Docs/`
2. Refresh Files app (pull down to refresh)
3. Restart Files app
4. Check storage permissions: `termux-setup-storage`

### "No write permission to /sdcard/"

**Solution**: Run storage setup again
```bash
termux-setup-storage
```

---

## Batch Processing

Generate documentation for multiple models at once:

```bash
#!/bin/bash
# Save as: scrape_all.sh

cd ~/aiml-scraper

models=(
    "gpt-4o"
    "gpt-4o-mini"
    "claude-3-sonnet"
    "deepseek-chat"
    "gemini-2.0-flash"
)

for model in "${models[@]}"; do
    echo "Scraping $model..."
    ./aiml_scraper_mobile.sh "$model"
    echo "Done: $model"
    sleep 2
done

echo "All done! Check /sdcard/AIML_API_Docs/ in your Files app"
```

Run with:
```bash
chmod +x scrape_all.sh
./scrape_all.sh
```

---

## Performance Tips

### For Limited Storage:
```bash
# Clear cache to free up space
rm -rf /sdcard/AIML_API_Docs/.cache

# This won't delete your context.md files, just cached HTML
```

### For Faster Scraping:
- Use bash script (faster than Python)
- Cache is reused automatically
- Run one model at a time

### For Limited Data:
- Use smaller models for testing
- Cache reduces repeated downloads
- Bash script uses less memory

---

## Advanced: Automate with Cron

You can schedule automatic scraping (if you have a rooted device or use Tasker):

```bash
# Example: Scrape daily at 2 AM
# (Requires additional setup with Tasker or similar)

# In Termux, you can use at command:
echo "./aiml_scraper_mobile.sh gpt-4o" | at 02:00
```

---

## Quick Reference

```bash
# First time setup
termux-setup-storage
pkg update && pkg upgrade -y
pkg install -y curl jq python3
pip install requests beautifulsoup4

# Download scripts
mkdir -p ~/aiml-scraper && cd ~/aiml-scraper
# Copy scripts here and chmod +x them

# Generate documentation
./aiml_scraper_mobile.sh gpt-4o

# Access files
# Open Files app → Internal Storage → AIML_API_Docs

# Share with AI
# Open file in Files app → Share → Choose AI app
```

---

## What You Get

Each generated `context.md` file contains:

✅ Complete API endpoints  
✅ All parameters (required & optional)  
✅ Authentication setup  
✅ Code examples (Python, JavaScript, cURL, Bash)  
✅ Error handling strategies  
✅ Rate limiting info  
✅ Cost optimization tips  

Perfect for sharing with AI assistants to help build scripts and pipelines!

---

## Supported Models

| Provider | Examples |
|----------|----------|
| OpenAI | gpt-4o, gpt-4o-mini, o1, o3 |
| Anthropic | claude-3-sonnet, claude-3-opus |
| DeepSeek | deepseek-chat, deepseek-coder |
| Google | gemini-2.0-flash, gemini-pro |
| Mistral | mistral-large, mistral-small |
| Meta | llama-2-70b |
| Alibaba | qwen-max, qwen-turbo |
| Moonshot | moonshot-v1 |
| Cohere | command-r-plus |
| xAI | grok-2 |

---

## Support

If you run into issues:

1. **Check Termux permissions**: `termux-setup-storage`
2. **Verify internet**: `ping google.com`
3. **Test script**: `./aiml_scraper_mobile.sh gpt-4o`
4. **Check files**: `ls -la /sdcard/AIML_API_Docs/`
5. **Refresh Files app**: Pull down to refresh

---

## Next Steps

1. ✅ Generate context files for models you use
2. ✅ Share with your AI assistant
3. ✅ Ask AI to help build scripts using the context
4. ✅ Use the generated documentation for API integration
5. ✅ Bookmark this guide for future reference

---

**Version**: 1.0  
**Last Updated**: 2025-12-10  
**Device**: Pixel 9a with Termux  
**Storage**: /sdcard/AIML_API_Docs/  
**Access**: Via phone's native Files app
