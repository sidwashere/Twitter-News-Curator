"""
Twitter News Curator - Main Module
Orchestrates the news curation and posting workflow
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from news_fetcher import NewsFetcher
from tweet_generator import TweetGenerator
from article_tracker import ArticleTracker
from twitter_poster import TwitterPoster

# Setup logging
def setup_logging():
    """Configure logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"curator_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)


class TwitterNewsCurator:
    """Main class orchestrating the news curation workflow"""
    
    def __init__(self, auto_post: bool = False):
        """
        Initialize the Twitter News Curator
        
        Args:
            auto_post: If True, automatically post tweets without review
        """
        logger.info("=" * 60)
        logger.info("Twitter News Curator - Initializing")
        logger.info("=" * 60)
        
        # Load environment variables
        load_dotenv()
        
        self.auto_post = auto_post
        
        # Initialize components
        try:
            self.fetcher = NewsFetcher()
            self.tracker = ArticleTracker()
            
            gemini_key = os.getenv('GEMINI_API_KEY')
            if not gemini_key:
                raise ValueError("GEMINI_API_KEY not found in .env file")
            
            self.generator = TweetGenerator(gemini_key)
            
            # Initialize Twitter poster if credentials available
            if self._has_twitter_credentials():
                self.poster = TwitterPoster(
                    api_key=os.getenv('X_API_KEY'),
                    api_secret=os.getenv('X_API_SECRET'),
                    access_token=os.getenv('X_ACCESS_TOKEN'),
                    access_secret=os.getenv('X_ACCESS_SECRET')
                )
            else:
                self.poster = None
                logger.warning("Twitter credentials not found - running in draft mode only")
            
            logger.info("✅ Initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {str(e)}")
            raise
    
    def _has_twitter_credentials(self) -> bool:
        """Check if Twitter credentials are available"""
        required = ['X_API_KEY', 'X_API_SECRET', 'X_ACCESS_TOKEN', 'X_ACCESS_SECRET']
        return all(os.getenv(key) for key in required)
    
    def find_new_article(self):
        """
        Find a new article that hasn't been posted yet
        
        Returns:
            Article dictionary or None
        """
        logger.info("Fetching latest articles...")
        articles = self.fetcher.fetch_latest_articles(limit=10)
        
        for article in articles:
            if not self.tracker.has_been_posted(article['link']):
                logger.info(f"✅ Found new article: {article['title']}")
                return article
        
        logger.warning("No new articles found (all have been posted)")
        return None
    
    def generate_draft(self, article):
        """
        Generate a tweet draft for an article
        
        Args:
            article: Article dictionary
            
        Returns:
            Tuple of (tweet_content, full_tweet) or (None, None)
        """
        logger.info(f"Generating tweet for: {article['title']}")
        
        tweet_content = self.generator.generate_tweet(article)
        
        if not tweet_content:
            logger.error("Failed to generate tweet")
            return None, None
        
        full_tweet = self.generator.format_final_tweet(tweet_content, article['link'])
        
        return tweet_content, full_tweet
    
    def post_tweet(self, full_tweet: str, article):
        """
        Post a tweet and track the article
        
        Args:
            full_tweet: Complete tweet text with hashtags and link
            article: Article dictionary
            
        Returns:
            Tweet ID or None
        """
        if not self.poster:
            logger.error("Cannot post - Twitter credentials not configured")
            return None
        
        tweet_id = self.poster.post_tweet(full_tweet)
        
        if tweet_id:
            self.tracker.mark_as_posted(article, tweet_id)
            logger.info(f"✅ Tweet posted and tracked: {tweet_id}")
        
        return tweet_id
    
    def run_once(self):
        """
        Run one iteration: find article, generate tweet, post (if auto_post)
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("\n" + "=" * 60)
        logger.info("Starting new curation cycle")
        logger.info("=" * 60 + "\n")
        
        # Find new article
        article = self.find_new_article()
        if not article:
            return False
        
        print(f"\n📰 Article: {article['title']}")
        print(f"🔗 Link: {article['link']}")
        print(f"📝 Summary: {article['summary'][:150]}...\n")
        
        # Generate tweet
        tweet_content, full_tweet = self.generate_draft(article)
        if not full_tweet:
            return False
        
        print(f"🤖 Generated Tweet ({len(full_tweet)} chars):")
        print("-" * 60)
        print(full_tweet)
        print("-" * 60 + "\n")
        
        # Post or save draft
        if self.auto_post:
            logger.info("AUTO_POST enabled - posting immediately")
            tweet_id = self.post_tweet(full_tweet, article)
            return tweet_id is not None
        else:
            logger.info("Manual review required (AUTO_POST=false)")
            print("ℹ️  Tweet saved as draft. Set AUTO_POST=true to post automatically.")
            
            if self.poster:
                response = input("\n📤 Post this tweet now? (y/n): ")
                if response.lower() == 'y':
                    tweet_id = self.post_tweet(full_tweet, article)
                    return tweet_id is not None
                else:
                    print("✋ Tweet not posted")
                    # Still mark as "drafted" to avoid regenerating
                    self.tracker.mark_as_posted(article, tweet_id=None)
            
            return True


def main():
    """Main entry point"""
    setup_logging()
    
    # Check for auto-post setting
    auto_post = os.getenv('AUTO_POST', 'false').lower() == 'true'
    
    try:
        curator = TwitterNewsCurator(auto_post=auto_post)
        curator.run_once()
        
    except KeyboardInterrupt:
        logger.info("\n\n⏸️  Stopped by user")
    except Exception as e:
        logger.error(f"\n\n❌ Error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
