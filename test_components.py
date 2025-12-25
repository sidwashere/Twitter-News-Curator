"""
Test script to debug the bot components individually
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Load environment
load_dotenv()

print("=" * 60)
print("Twitter News Curator - Component Test")
print("=" * 60)
print()

# Test 1: RSS Feed Fetcher
print("1️⃣ Testing RSS Feed Fetcher...")
print("-" * 60)
try:
    from news_fetcher import NewsFetcher
    fetcher = NewsFetcher()
    articles = fetcher.fetch_latest_articles(limit=3)
    
    if articles:
        print(f"✅ SUCCESS: Fetched {len(articles)} articles")
        print(f"\nSample article:")
        print(f"  Title: {articles[0]['title']}")
        print(f"  Link: {articles[0]['link'][:60]}...")
    else:
        print("❌ FAILED: No articles fetched")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print()

# Test 2: Article Tracker
print("2️⃣ Testing Article Tracker...")
print("-" * 60)
try:
    from article_tracker import ArticleTracker
    tracker = ArticleTracker()
    count = tracker.get_posted_count()
    print(f"✅ SUCCESS: Tracking {count} posted articles")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print()

# Test 3: Tweet Generator (Gemini AI)
print("3️⃣ Testing Tweet Generator...")
print("-" * 60)
try:
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("❌ FAILED: GEMINI_API_KEY not found in .env")
    else:
        from tweet_generator import TweetGenerator
        generator = TweetGenerator(gemini_key)
        
        test_article = {
            'title': 'Test Article: New AI Breakthrough in Natural Language',
            'summary': 'Researchers announce significant advances in AI language models.',
            'link': 'https://example.com/test'
        }
        
        print(f"Generating tweet for: {test_article['title']}")
        tweet_content = generator.generate_tweet(test_article)
        
        if tweet_content:
            full_tweet = generator.format_final_tweet(tweet_content, test_article['link'])
            print(f"✅ SUCCESS: Generated tweet ({len(full_tweet)} chars)")
            print(f"\nGenerated tweet:")
            print("-" * 60)
            print(full_tweet)
            print("-" * 60)
        else:
            print("❌ FAILED: Could not generate tweet")
            
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Twitter Poster  
print("4️⃣ Testing Twitter Authentication...")
print("-" * 60)
try:
    api_key = os.getenv('X_API_KEY')
    api_secret = os.getenv('X_API_SECRET')
    access_token = os.getenv('X_ACCESS_TOKEN')
    access_secret = os.getenv('X_ACCESS_SECRET')
    
    if not all([api_key, api_secret, access_token, access_secret]):
        print("❌ FAILED: Twitter credentials not complete in .env")
    else:
        from twitter_poster import TwitterPoster
        poster = TwitterPoster(api_key, api_secret, access_token, access_secret)
        print(f"✅ SUCCESS: Authenticated as @{poster.username}")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print("\nPossible causes:")
    print("  - Invalid API credentials")
    print("  - App permissions not set to 'Read and Write'")
    print("  - Access tokens not regenerated after changing permissions")
    print("  - Free tier limitations")

print()
print("=" * 60)
print("Test Complete")
print("=" * 60)
