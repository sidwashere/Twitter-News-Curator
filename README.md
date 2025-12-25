# Twitter News Curator 🤖

An AI-powered bot that curates tech news from RSS feeds and posts engaging tweets to X/Twitter using Google Gemini AI.

## ✨ Features

- 📰 Fetches latest tech news from multiple RSS feeds
- 🤖 Generates engaging, human-like tweets using Google Gemini AI
- 🔄 Prevents duplicate posts with smart tracking
- 👤 Human-in-the-loop review before posting
- 📊 Comprehensive logging and error handling
- 🆓 Works with free-tier APIs (X/Twitter & Google Gemini)

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- X/Twitter Developer Account ([Apply here](https://developer.twitter.com/))
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))

### 2. Installation

```bash
# Clone or download the project
cd "Twitter News Curator"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

**Copy the environment template:**
```bash
copy .env.template .env
```

**Edit `.env` and add your API credentials:**
```env
# Twitter/X API Credentials
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_SECRET=your_access_token_secret_here

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Bot Settings
AUTO_POST=false  # Set to 'true' for automatic posting
MAX_TWEETS_PER_DAY=10
```

**Customize RSS feeds** (optional):
Edit `config/config.json` to add/remove news sources and adjust tweet style.

### 4. Run the Bot

**Generate and review a tweet draft:**
```bash
python run.py
```

The bot will:
1. Fetch the latest tech news
2. Find an article you haven't posted about
3. Generate an engaging tweet using AI
4. Show you the draft for review
5. Ask if you want to post it

**Enable automatic posting:**
Set `AUTO_POST=true` in `.env` file for hands-off operation.

## 📁 Project Structure

```
Twitter News Curator/
├── src/
│   ├── news_fetcher.py      # RSS feed fetcher
│   ├── tweet_generator.py   # AI tweet generator
│   ├── article_tracker.py   # Duplicate prevention
│   └── twitter_poster.py    # X/Twitter API integration
├── config/
│   └── config.json          # Bot configuration
├── data/
│   └── posted_articles.json # Tracking posted articles
├── logs/                    # Log files
├── scripts/
│   ├── update-context.ps1   # Auto-update context
│   └── setup-scheduler.ps1  # Schedule context updates
├── run.py                   # Main entry point
├── requirements.txt         # Python dependencies
├── .env.template           # Environment variables template
└── README.md               # This file
```

## 🎯 Usage Examples

### Test Individual Components

**Test RSS fetching:**
```bash
python src/news_fetcher.py
```

**Test tweet generation** (requires GEMINI_API_KEY):
```bash
python src/tweet_generator.py
```

**Test Twitter posting** (requires Twitter credentials):
```bash
python src/twitter_poster.py
```

**Test article tracking:**
```bash
python src/article_tracker.py
```

### Run in Different Modes

**Draft mode** (review before posting):
```bash
python run.py
```

**Auto-post mode** (set in `.env`):
```env
AUTO_POST=true
```

## ⚙️ Configuration

### RSS Feeds

Edit `config/config.json` to customize news sources:

```json
{
  "rss_feeds": [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://venturebeat.com/category/ai/feed/"
  ]
}
```

### Tweet Style

Customize hashtags, emoji usage, and more:

```json
{
  "tweet_style": {
    "hashtags": ["#AI", "#Tech", "#Innovation"],
    "max_hashtags": 2,
    "include_emoji": true,
    "max_length": 280
  }
}
```

### AI Settings

Adjust Gemini model and temperature:

```json
{
  "ai_settings": {
    "model": "gemini-1.5-flash",
    "temperature": 0.9,
    "max_retries": 3
  }
}
```

## 📅 Automation

### Schedule with Windows Task Scheduler

Create a daily scheduled task:

```powershell
# Create a scheduled task to run daily at 9 AM
schtasks /create /tn "TwitterNewsCurator" /tr "python run.py" /sc daily /st 09:00
```

### Schedule with Cron (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/Twitter\ News\ Curator && /path/to/venv/bin/python run.py
```

### GitHub Actions (Optional)

See `.github/workflows/tweet-scheduler.yml` for automated cloud execution.

## 🛡️ Safety & Best Practices

1. **Start with `AUTO_POST=false`** - Review tweets before posting
2. **Limit posting frequency** - Respect X/Twitter rate limits (max 50 tweets/day for free tier)
3. **Monitor your account** - Check for spam flags or engagement issues
4. **Add human touch** - Review and edit AI-generated tweets occasionally
5. **Diversify content** - Add your own commentary to generated tweets

## 📊 Monitoring

Check logs in the `logs/` directory:

```bash
# View today's log
tail -f logs/curator_20231225.log
```

## 🐛 Troubleshooting

### "Twitter authentication failed"
- Verify your API credentials in `.env`
- Ensure you have "Read and Write" permissions in Twitter Developer Portal
- Check if your developer account is approved

### "GEMINI_API_KEY not found"
- Copy `.env.template` to `.env`
- Add your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### "No new articles found"
- Check RSS feeds are accessible
- Clear article tracking: delete `data/posted_articles.json`
- Verify `config/config.json` contains valid RSS URLs

### "Tweet too long"
- AI automatically generates tweets under 280 chars
- If issues persist, adjust `temperature` in `config/config.json`

## 📝 License

This project is open source and available for personal and educational use.

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new RSS feeds
- Improve tweet generation prompts
- Add new features
- Fix bugs

## ⚠️ Disclaimer

This bot is for educational purposes. Always comply with X/Twitter's Terms of Service and automation rules. Excessive automation may result in account suspension.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `logs/` directory
3. Test individual components
4. Ensure all API credentials are valid

---

**Happy curating! 🚀**
