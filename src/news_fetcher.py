"""
Twitter News Curator - News Fetcher Module
Fetches latest articles from configured RSS feeds
"""

import feedparser
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetches and parses RSS feeds for tech news"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize NewsFetcher with configuration
        
        Args:
            config_path: Path to configuration JSON file
        """
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.rss_feeds = self.config.get('rss_feeds', [])
        logger.info(f"Initialized with {len(self.rss_feeds)} RSS feeds")
    
    def fetch_latest_articles(self, limit: int = 10) -> List[Dict]:
        """
        Fetch latest articles from all configured RSS feeds
        
        Args:
            limit: Maximum number of articles to return per feed
            
        Returns:
            List of article dictionaries with title, summary, link, published
        """
        all_articles = []
        
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"Fetching from: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
                
                for entry in feed.entries[:limit]:
                    article = self._parse_entry(entry, feed_url)
                    if article:
                        all_articles.append(article)
                
                logger.info(f"Fetched {len(feed.entries[:limit])} articles from {feed_url}")
                
            except Exception as e:
                logger.error(f"Error fetching feed {feed_url}: {str(e)}")
                continue
        
        # Sort by published date (most recent first)
        all_articles.sort(key=lambda x: x.get('published_parsed', 0), reverse=True)
        
        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def _parse_entry(self, entry, source_url: str) -> Optional[Dict]:
        """
        Parse a single RSS entry into article format
        
        Args:
            entry: feedparser entry object
            source_url: Source RSS feed URL
            
        Returns:
            Article dictionary or None if parsing fails
        """
        try:
            # Extract published date
            published = entry.get('published', '')
            published_parsed = entry.get('published_parsed', None)
            
            # Get summary/description
            summary = entry.get('summary', entry.get('description', ''))
            
            # Clean HTML tags from summary if present
            if summary:
                import re
                summary = re.sub('<[^<]+?>', '', summary)
                summary = summary.strip()[:500]  # Limit length
            
            article = {
                'title': entry.get('title', '').strip(),
                'link': entry.get('link', '').strip(),
                'summary': summary,
                'published': published,
                'published_parsed': published_parsed,
                'source': source_url,
                'fetched_at': datetime.now().isoformat()
            }
            
            # Validate required fields
            if not article['title'] or not article['link']:
                logger.warning(f"Skipping article with missing title or link")
                return None
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing entry: {str(e)}")
            return None
    
    def get_article_by_url(self, url: str) -> Optional[Dict]:
        """
        Fetch a specific article by URL
        
        Args:
            url: Article URL to fetch
            
        Returns:
            Article dictionary or None if not found
        """
        articles = self.fetch_latest_articles(limit=50)
        for article in articles:
            if article['link'] == url:
                return article
        return None


if __name__ == "__main__":
    # Test the news fetcher
    logging.basicConfig(level=logging.INFO)
    
    fetcher = NewsFetcher()
    articles = fetcher.fetch_latest_articles(limit=3)
    
    print(f"\n✅ Fetched {len(articles)} articles\n")
    
    for i, article in enumerate(articles[:3], 1):
        print(f"{i}. {article['title']}")
        print(f"   Link: {article['link']}")
        print(f"   Summary: {article['summary'][:100]}...")
        print()
