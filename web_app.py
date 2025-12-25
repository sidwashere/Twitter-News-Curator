"""
Twitter News Curator - Web Dashboard
Flask web application for managing the bot
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import secrets

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from news_fetcher import NewsFetcher
from tweet_generator import TweetGenerator
from article_tracker import ArticleTracker
from twitter_poster import TwitterPoster

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Initialize bot components
logger.info("Initializing bot components...")
fetcher = NewsFetcher()
tracker = ArticleTracker()

gemini_key = os.getenv('GEMINI_API_KEY')
generator = TweetGenerator(gemini_key) if gemini_key else None

# Initialize Twitter poster if credentials available
twitter_creds = [
    os.getenv('X_API_KEY'),
    os.getenv('X_API_SECRET'),
    os.getenv('X_ACCESS_TOKEN'),
    os.getenv('X_ACCESS_SECRET')
]
poster = TwitterPoster(*twitter_creds) if all(twitter_creds) else None


@app.route('/')
def dashboard():
    """Main dashboard"""
    stats = {
        'total_posted': tracker.get_posted_count(),
        'rss_feeds': len(fetcher.rss_feeds),
        'twitter_connected': poster is not None,
        'ai_connected': generator is not None
    }
    
    recent_posts = tracker.get_recent_posts(limit=5)
    
    return render_template('dashboard.html', stats=stats, recent_posts=recent_posts)


@app.route('/articles')
def articles():
    """Browse fetched articles"""
    limit = int(request.args.get('limit', 20))
    articles_list = fetcher.fetch_latest_articles(limit=limit)
    
    # Mark which ones are posted
    for article in articles_list:
        article['is_posted'] = tracker.has_been_posted(article['link'])
    
    # Pass config for source selection
    config = {
        'rss_feeds': fetcher.rss_feeds
    }
    
    return render_template('articles.html', articles=articles_list, config=config)


@app.route('/api/fetch-articles', methods=['POST'])
def fetch_articles_api():
    """Manually fetch articles from selected sources"""
    try:
        data = request.json
        selected_sources = data.get('sources', fetcher.rss_feeds)
        limit = data.get('limit', 20)
        
        logger.info(f"Fetching articles from {len(selected_sources)} sources, limit={limit}")
        
        # Temporarily update sources
        original_feeds = fetcher.rss_feeds
        fetcher.rss_feeds = selected_sources
        
        # Fetch articles
        articles_list = fetcher.fetch_latest_articles(limit=limit)
        
        # Restore original feeds
        fetcher.rss_feeds = original_feeds
        
        # Mark which ones are posted
        for article in articles_list:
            article['is_posted'] = tracker.has_been_posted(article['link'])
        
        logger.info(f"Fetched {len(articles_list)} articles from {len(selected_sources)} sources")
        
        return jsonify({
            'success': True,
            'articles': articles_list,
            'count': len(articles_list)
        })
    
    except Exception as e:
        logger.error(f"Error fetching articles: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-tweet', methods=['POST'])
def generate_tweet_api():
    """Generate tweet for an article"""
    try:
        data = request.json
        article_url = data.get('article_url')
        
        logger.info(f"Generate tweet request for: {article_url}")
        
        if not article_url:
            return jsonify({'error': 'article_url is required'}), 400
        
        # Fetch articles and find the one
        articles = fetcher.fetch_latest_articles(limit=50)
        article = next((a for a in articles if a['link'] == article_url), None)
        
        if not article:
            logger.error(f"Article not found: {article_url}")
            return jsonify({'error': 'Article not found'}), 404
        
        if not generator:
            logger.error("AI generator not initialized")
            return jsonify({'error': 'AI not configured. Check GEMINI_API_KEY in .env file.'}), 500
        
        # Generate tweet
        logger.info("Generating tweet with AI...")
        tweet_content = generator.generate_tweet(article)
        
        if not tweet_content:
            logger.error("Tweet generation returned empty")
            return jsonify({'error': 'Failed to generate tweet'}), 500
        
        full_tweet = generator.format_final_tweet(tweet_content, article['link'])
        logger.info(f"Tweet generated successfully: {len(full_tweet)} chars")
        
        # Store in session for posting
        session['current_article'] = article
        session['current_tweet'] = full_tweet
        session['current_content'] = tweet_content
        
        return jsonify({
            'content': tweet_content,
            'full_tweet': full_tweet,
            'char_count': len(full_tweet),
            'article': article
        })
    
    except Exception as e:
        logger.error(f"Error in generate_tweet_api: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/regenerate-tweet', methods=['POST'])
def regenerate_tweet():
    """Regenerate tweet with different parameters"""
    try:
        data = request.json
        article = session.get('current_article')
        
        if not article:
            return jsonify({'error': 'No article in session. Please generate a tweet first.'}), 400
        
        if not generator:
            return jsonify({'error': 'AI not configured. Check GEMINI_API_KEY.'}), 500
        
        # Apply custom parameters
        temperature = float(data.get('temperature', 0.9))
        tone = data.get('tone', 'default')
        
        # Log the regeneration request
        print(f"Regenerating tweet for article: {article.get('title', 'Unknown')[:50]}...")
        print(f"Parameters: tone={tone}, temperature={temperature}")
        
        # Generate new tweet
        tweet_content = generator.generate_tweet(article, temperature=temperature)
        
        if not tweet_content:
            return jsonify({'error': 'Failed to generate tweet. AI returned empty response.'}), 500
        
        full_tweet = generator.format_final_tweet(tweet_content, article['link'])
        
        # Update session
        session['current_tweet'] = full_tweet
        session['current_content'] = tweet_content
        
        print(f"Regenerated tweet: {tweet_content[:50]}...")
        
        return jsonify({
            'content': tweet_content,
            'full_tweet': full_tweet,
            'char_count': len(full_tweet),
            'success': True
        })
    
    except Exception as e:
        error_msg = f"Error regenerating tweet: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': error_msg,
            'success': False
        }), 500


@app.route('/api/post-tweet', methods=['POST'])
def post_tweet_api():
    """Post the current tweet"""
    full_tweet = session.get('current_tweet')
    article = session.get('current_article')
    
    if not full_tweet or not article:
        return jsonify({'error': 'No tweet ready to post'}), 400
    
    if not poster:
        return jsonify({'error': 'Twitter not configured'}), 500
    
    # Allow editing
    data = request.json
    edited_tweet = data.get('tweet', full_tweet)
    
    # Post
    tweet_id = poster.post_tweet(edited_tweet)
    
    if tweet_id:
        tracker.mark_as_posted(article, tweet_id)
        
        return jsonify({
            'success': True,
            'tweet_id': tweet_id,
            'url': f"https://twitter.com/{poster.username}/status/{tweet_id}"
        })
    else:
        return jsonify({'error': 'Failed to post tweet'}), 500


@app.route('/draft')
def draft_view():
    """View current draft"""
    article = session.get('current_article')
    tweet = session.get('current_tweet')
    content = session.get('current_content')
    
    if not article or not tweet:
        return render_template('draft.html', error="No draft available")
    
    return render_template('draft.html', article=article, tweet=tweet, content=content)


@app.route('/history')
def history():
    """Posting history"""
    limit = int(request.args.get('limit', 50))
    posts = tracker.get_recent_posts(limit=limit)
    
    return render_template('history.html', posts=posts)


@app.route('/settings')
def settings():
    """Bot settings and configuration"""
    config = {
        'rss_feeds': fetcher.rss_feeds,
        'ai_model': generator.model.model_name if generator else None,
        'twitter_username': poster.username if poster else None,
        'auto_post': os.getenv('AUTO_POST', 'false')
    }
    
    return render_template('settings.html', config=config)


@app.route('/monitor')
def monitor():
    """Backend monitoring dashboard"""
    stats = {
        'total_posted': tracker.get_posted_count(),
        'rss_feeds': len(fetcher.rss_feeds),
        'twitter_connected': poster is not None,
        'ai_connected': generator is not None
    }
    
    return render_template('monitor.html', stats=stats)


@app.route('/api/monitor/stats', methods=['GET'])
def monitor_stats():
    """Return live system statistics for monitor page"""
    try:
        import psutil
        import os
        from datetime import datetime
        
        # System stats
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        # Application stats
        posted_count = tracker.get_posted_count()
        
        # Get recent activity from logs
        recent_logs = []
        log_file = 'logs/bot.log'
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    recent_logs = lines[-10:]  # Last 10 log entries
            except:
                pass
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'disk_percent': round(disk.percent, 1),
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2)
            },
            'application': {
                'total_posts': posted_count,
                'rss_feeds_count': len(fetcher.rss_feeds),
                'twitter_connected': poster is not None,
                'ai_connected': generator is not None,
                'uptime': 'Active'
            },
            'recent_logs': [log.strip() for log in recent_logs if log.strip()]
        }
        
        return jsonify(stats)
    
    except Exception as e:
        print(f"Error getting monitor stats: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# ============= Settings API Endpoints =============

@app.route('/api/settings/save', methods=['POST'])
def save_settings():
    """Save settings to config file"""
    try:
        data = request.json
        
        # Load current config
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        # Update config with new settings
        if 'rss_feeds' in data:
            config['rss_feeds'] = data['rss_feeds']
        
        if 'topic_preferences' in data:
            config['topic_preferences'] = data['topic_preferences']
        
        if 'ai_settings' in data:
            config['ai_settings'].update(data['ai_settings'])
        
        if 'tweet_style' in data:
            config['tweet_style'].update(data['tweet_style'])
        
        if 'posting_schedule' in data:
            config['posting_schedule'].update(data['posting_schedule'])
        
        # Save to file
        with open('config/config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        # Reload components with new config
        reload_config()
        
        logger.info("Settings saved successfully")
        return jsonify({
            'success': True,
            'message': 'Settings saved and applied successfully'
        })
    
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rss/add', methods=['POST'])
def add_rss_feed():
    """Add new RSS feed"""
    try:
        data = request.json
        feed_url = data.get('url', '').strip()
        
        if not feed_url:
            return jsonify({
                'success': False,
                'error': 'Feed URL is required'
            }), 400
        
        # Load current config
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        # Check if feed already exists
        if feed_url in config['rss_feeds']:
            return jsonify({
                'success': False,
                'error': 'Feed already exists'
            }), 400
        
        # Add new feed
        config['rss_feeds'].append(feed_url)
        
        # Save to file
        with open('config/config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        # Reload config
        reload_config()
        
        logger.info(f"Added RSS feed: {feed_url}")
        return jsonify({
            'success': True,
            'message': 'RSS feed added successfully'
        })
    
    except Exception as e:
        logger.error(f"Error adding RSS feed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rss/remove', methods=['POST'])
def remove_rss_feed():
    """Remove RSS feed"""
    try:
        data = request.json
        feed_url = data.get('url', '').strip()
        
        # Load current config
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        # Remove feed
        if feed_url in config['rss_feeds']:
            config['rss_feeds'].remove(feed_url)
            
            # Save to file
            with open('config/config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
            # Reload config
            reload_config()
            
            logger.info(f"Removed RSS feed: {feed_url}")
            return jsonify({
                'success': True,
                'message': 'RSS feed removed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Feed not found'
            }), 404
    
    except Exception as e:
        logger.error(f"Error removing RSS feed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def reload_config():
    """Reload configuration in all components without restart"""
    global fetcher, generator
    
    try:
        # Reload RSS feeds
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        fetcher.rss_feeds = config['rss_feeds']
        logger.info(f"Reloaded {len(fetcher.rss_feeds)} RSS feeds")
        
        # Reload AI settings
        if generator:
            generator.config = config
            generator.tweet_style = config.get('tweet_style', {})
            generator.temperature = config.get('ai_settings', {}).get('temperature', 0.9)
            logger.info("Reloaded AI settings")
        
        logger.info("✅ Configuration reloaded successfully")
        
    except Exception as e:
        logger.error(f"Error reloading config: {str(e)}")


if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Twitter News Curator - Web Dashboard")
    print("=" * 70)
    print(f"\n📊 Status:")
    print(f"  RSS Feeds: {len(fetcher.rss_feeds)} configured")
    print(f"  AI: {'✅ Connected' if generator else '❌ Not configured'}")
    print(f"  Twitter: {'✅ Connected as @' + poster.username if poster else '❌ Not configured'}")
    print(f"  Posted Articles: {tracker.get_posted_count()}")
    print(f"\n🌐 Open in browser: http://localhost:5000")
    print("=" * 70)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
