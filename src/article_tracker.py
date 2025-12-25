"""
Twitter News Curator - Article Tracker Module
Tracks posted articles to prevent duplicates
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ArticleTracker:
    """Tracks posted articles to prevent duplicate tweets"""
    
    def __init__(self, data_file: str = "data/posted_articles.json"):
        """
        Initialize ArticleTracker
        
        Args:
            data_file: Path to JSON file storing posted articles
        """
        self.data_file = Path(data_file)
        self.posted_articles = self._load_data()
        logger.info(f"Loaded {len(self.posted_articles)} posted articles")
    
    def _load_data(self) -> Dict:
        """Load posted articles from JSON file"""
        if not self.data_file.exists():
            logger.info(f"Creating new tracking file: {self.data_file}")
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            return {}
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Error loading data file: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error loading data: {e}")
            return {}
    
    def _save_data(self):
        """Save posted articles to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.posted_articles, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(self.posted_articles)} articles to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving data file: {e}")
    
    def has_been_posted(self, article_url: str) -> bool:
        """
        Check if an article has already been posted
        
        Args:
            article_url: URL of the article to check
            
        Returns:
            True if article has been posted, False otherwise
        """
        return article_url in self.posted_articles
    
    def mark_as_posted(self, article: Dict, tweet_id: Optional[str] = None):
        """
        Mark an article as posted
        
        Args:
            article: Article dictionary with title, link, etc.
            tweet_id: Twitter/X tweet ID (if posted)
        """
        article_url = article.get('link', '')
        
        if not article_url:
            logger.warning("Cannot mark article without URL")
            return
        
        self.posted_articles[article_url] = {
            'title': article.get('title', ''),
            'posted_at': datetime.now().isoformat(),
            'tweet_id': tweet_id,
            'source': article.get('source', '')
        }
        
        self._save_data()
        logger.info(f"Marked as posted: {article.get('title', '')[:50]}...")
    
    def get_posted_count(self) -> int:
        """Get total number of posted articles"""
        return len(self.posted_articles)
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict]:
        """
        Get recently posted articles
        
        Args:
            limit: Maximum number of articles to return
            
        Returns:
            List of recently posted articles
        """
        # Sort by posted_at date
        sorted_articles = sorted(
            self.posted_articles.items(),
            key=lambda x: x[1].get('posted_at', ''),
            reverse=True
        )
        
        return [
            {'url': url, **data}
            for url, data in sorted_articles[:limit]
        ]
    
    def cleanup_old_entries(self, max_entries: int = 1000):
        """
        Remove oldest entries if tracking file gets too large
        
        Args:
            max_entries: Maximum number of entries to keep
        """
        if len(self.posted_articles) <= max_entries:
            return
        
        logger.info(f"Cleaning up old entries (keeping {max_entries} most recent)")
        
        # Sort by posted_at date
        sorted_articles = sorted(
            self.posted_articles.items(),
            key=lambda x: x[1].get('posted_at', ''),
            reverse=True
        )
        
        # Keep only the most recent entries
        self.posted_articles = dict(sorted_articles[:max_entries])
        self._save_data()
        
        logger.info(f"Cleanup complete. Now tracking {len(self.posted_articles)} articles")
    
    def clear_all(self):
        """Clear all tracked articles (use with caution!)"""
        logger.warning("Clearing all tracked articles")
        self.posted_articles = {}
        self._save_data()


if __name__ == "__main__":
    # Test the article tracker
    logging.basicConfig(level=logging.INFO)
    
    tracker = ArticleTracker()
    
    # Test article
    test_article = {
        'title': 'Test AI News Article',
        'link': 'https://example.com/test-article',
        'source': 'https://example.com/rss'
    }
    
    print(f"Total posted: {tracker.get_posted_count()}")
    print(f"Has been posted: {tracker.has_been_posted(test_article['link'])}")
    
    # Mark as posted
    tracker.mark_as_posted(test_article, tweet_id="123456789")
    
    print(f"After posting:")
    print(f"Has been posted: {tracker.has_been_posted(test_article['link'])}")
    print(f"Total posted: {tracker.get_posted_count()}")
    
    # Show recent posts
    print("\nRecent posts:")
    for post in tracker.get_recent_posts(limit=5):
        print(f"  - {post['title']}")
