"""
Twitter News Curator - Twitter Poster Module
Handles posting tweets to X/Twitter using Tweepy
"""

import tweepy
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TwitterPoster:
    """Posts tweets to X/Twitter"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_secret: str):
        """
        Initialize TwitterPoster with API credentials
        
        Args:
            api_key: X API key
            api_secret: X API secret
            access_token: X access token
            access_secret: X access token secret
        """
        try:
            # Initialize Tweepy client (v2 API)
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret
            )
            
            # Test authentication
            me = self.client.get_me()
            logger.info(f"✅ Authenticated as: @{me.data.username}")
            self.username = me.data.username
            
        except Exception as e:
            logger.error(f"❌ Twitter authentication failed: {str(e)}")
            raise
    
    def post_tweet(self, text: str) -> Optional[str]:
        """
        Post a tweet
        
        Args:
            text: Tweet text (max 280 characters)
            
        Returns:
            Tweet ID if successful, None otherwise
        """
        if len(text) > 280:
            logger.error(f"Tweet too long: {len(text)} characters (max: 280)")
            return None
        
        try:
            logger.info(f"Posting tweet ({len(text)} chars)...")
            response = self.client.create_tweet(text=text)
            
            tweet_id = response.data['id']
            logger.info(f"✅ Tweet posted successfully! ID: {tweet_id}")
            logger.info(f"   URL: https://twitter.com/{self.username}/status/{tweet_id}")
            
            return tweet_id
            
        except tweepy.errors.TweepyException as e:
            logger.error(f"❌ Failed to post tweet: {str(e)}")
            
            # Handle rate limiting
            if hasattr(e, 'response') and e.response:
                if e.response.status_code == 429:
                    logger.error("Rate limit exceeded. Please wait before posting again.")
                elif e.response.status_code == 403:
                    logger.error("Forbidden. Check your API permissions and account status.")
            
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error posting tweet: {str(e)}")
            return None
    
    def get_rate_limit_status(self) -> dict:
        """
        Get current rate limit status
        
        Returns:
            Dictionary with rate limit information
        """
        try:
            # Note: This uses v1.1 API endpoint
            # You may need OAuth 1.0a auth for this
            logger.info("Checking rate limit status...")
            return {"status": "Rate limit check not implemented for v2 API"}
        except Exception as e:
            logger.error(f"Error checking rate limits: {str(e)}")
            return {}
    
    def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet
        
        Args:
            tweet_id: ID of tweet to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Deleting tweet {tweet_id}...")
            self.client.delete_tweet(tweet_id)
            logger.info("✅ Tweet deleted successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete tweet: {str(e)}")
            return False


if __name__ == "__main__":
    # Test the Twitter poster
    import os
    from dotenv import load_dotenv
    
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    
    # Get credentials from environment
    api_key = os.getenv('X_API_KEY')
    api_secret = os.getenv('X_API_SECRET')
    access_token = os.getenv('X_ACCESS_TOKEN')
    access_secret = os.getenv('X_ACCESS_SECRET')
    
    if not all([api_key, api_secret, access_token, access_secret]):
        print("❌ Missing Twitter API credentials in .env file")
        print("Required: X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET")
        exit(1)
    
    try:
        poster = TwitterPoster(api_key, api_secret, access_token, access_secret)
        
        # Test tweet
        test_tweet = "🤖 Testing the Twitter News Curator bot! This is a test tweet. #AI #Tech"
        
        print(f"\nTest tweet: {test_tweet}")
        print(f"Length: {len(test_tweet)} chars\n")
        
        confirm = input("Post this test tweet? (y/n): ")
        
        if confirm.lower() == 'y':
            tweet_id = poster.post_tweet(test_tweet)
            if tweet_id:
                print(f"\n✅ Success! Tweet ID: {tweet_id}")
        else:
            print("Test cancelled")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
