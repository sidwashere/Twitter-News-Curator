"""
Twitter News Curator - Tweet Generator Module
Generates engaging tweets using Google Gemini AI
"""

import google.generativeai as genai
import json
import logging
import random
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class TweetGenerator:
    """Generates engaging tweets using AI"""
    
    def __init__(self, api_key: str, config_path: str = "config/config.json"):
        """
        Initialize TweetGenerator with Gemini API
        
        Args:
            api_key: Google Gemini API key
            config_path: Path to configuration JSON file
        """
        genai.configure(api_key=api_key)
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        ai_settings = self.config.get('ai_settings', {})
        model_name = ai_settings.get('model', 'gemini-1.5-flash')
        
        self.model = genai.GenerativeModel(model_name)
        self.tweet_style = self.config.get('tweet_style', {})
        self.max_length = self.tweet_style.get('max_length', 280)
        self.temperature = ai_settings.get('temperature', 0.9)
        
        logger.info(f"Initialized TweetGenerator with model: {model_name}")
    
    def generate_tweet(self, article: Dict, retry_count: int = 0) -> Optional[str]:
        """
        Generate an engaging tweet from an article
        
        Args:
            article: Article dictionary with title, summary, link
            retry_count: Current retry attempt
            
        Returns:
            Generated tweet text or None if generation fails
        """
        max_retries = self.config.get('ai_settings', {}).get('max_retries', 3)
        
        if retry_count >= max_retries:
            logger.error(f"Max retries ({max_retries}) reached for tweet generation")
            return None
        
        try:
            prompt = self._build_prompt(article)
            
            logger.info("Generating tweet with AI...")
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=150,
                )
            )
            
            tweet_text = response.text.strip()
            
            # Validate tweet
            if self._validate_tweet(tweet_text, article['link']):
                logger.info(f"✅ Generated tweet ({len(tweet_text)} chars)")
                return tweet_text
            else:
                logger.warning("Generated tweet failed validation, retrying...")
                return self.generate_tweet(article, retry_count + 1)
            
        except Exception as e:
            logger.error(f"Error generating tweet: {str(e)}")
            if retry_count < max_retries - 1:
                logger.info(f"Retrying... (attempt {retry_count + 2}/{max_retries})")
                return self.generate_tweet(article, retry_count + 1)
            return None
    
    def _build_prompt(self, article: Dict) -> str:
        """Build the AI prompt for tweet generation with rich content focus"""
        title = article.get('title', '')
        summary = article.get('summary', '')
        
        # Get style preferences
        max_hashtags = self.config.get('tweet_style', {}).get('max_hashtags', 1)
        
        prompt = f"""You are a tech thought leader writing an engaging tweet about breaking tech news.

ARTICLE CONTEXT:
Title: {title}
Summary: {summary}

YOUR MISSION: Write a compelling tweet that:
1. LEADS with an insight or hot take, NOT the news summary
2. Tells a mini-story or narrative arc
3. Connects to broader implications or trends
4. Sparks genuine conversation and debate
5. Feels human and conversational, not promotional

STRICT RULES:
- Target 200-240 characters (gives breathing room, not cramped)
- Start with a strong hook: "Here's why...", "Plot twist:", "Unpopular opinion:", "This changes everything:", etc.
- Use 1-2 sentences maximum - each should be COMPLETE thoughts
- Add the article link naturally at the end
- Use {max_hashtags or 0} hashtag{'s' if max_hashtags != 1 else ''} ONLY if genuinely relevant (less is more)
- NO generic phrases like "Check out", "Read more", "Just announced"
- NO cut-off sentences or trailing thoughts
- Write like you're texting a smart friend, not marketing to them

CONTENT STYLE OPTIONS (pick one naturally):
- Hot Take: Bold opinion that challenges assumptions
- Insight: "Here's what nobody is saying about..."  
- Data-driven: Lead with surprising numbers/stats
- Ironic: Witty observation about the situation
- Urgency: "This is happening faster than you think"
- Question: Thought-provoking question that demands discussion

GREAT EXAMPLES:
BAD: "Company X just launched new AI tool. Impressive features! #AI #Tech [link]"
GOOD: "Everyone's excited about AI that writes code. Meanwhile, nobody's asking who owns what it creates. [link]"

BAD: "Study shows 80% of developers prefer Python #Python #Dev [link]"  
GOOD: "Python devs: 80% majority. JavaScript devs: Still somehow running the world. How does this keep happening? [link]"

NOW WRITE: Create ONE tweet following all rules above. Do NOT include quotation marks around it. End with the link: {article.get('link', '')}"""

        return prompt
    
    def _validate_tweet(self, tweet_text: str, article_link: str) -> bool:
        """
        Validate generated tweet meets requirements
        
        Args:
            tweet_text: Generated tweet text
            article_link: Article URL to be appended
            
        Returns:
            True if valid, False otherwise
        """
        # Get hashtags
        all_hashtags = self.tweet_style.get('hashtags', ['#Tech', '#AI'])
        max_hashtags = self.tweet_style.get('max_hashtags', 2)
        selected_hashtags = random.sample(all_hashtags, min(max_hashtags, len(all_hashtags)))
        hashtags_str = ' '.join(selected_hashtags)
        
        # Build full tweet
        full_tweet = f"{tweet_text} {hashtags_str} {article_link}"
        
        # Check length
        if len(full_tweet) > self.max_length:
            logger.warning(f"Tweet too long: {len(full_tweet)} chars (max: {self.max_length})")
            return False
        
        # Check if tweet is too short
        if len(tweet_text.strip()) < 20:
            logger.warning("Tweet too short")
            return False
        
        # Check for common AI mistakes
        if tweet_text.startswith('"') or tweet_text.startswith('Tweet:'):
            logger.warning("Tweet has formatting issues")
            return False
        
        return True
    
    def format_final_tweet(self, content: str, article_link: str) -> str:
        """
        Format the final tweet with hashtags and link
        
        Args:
            content: Main tweet content
            article_link: Article URL
            
        Returns:
            Formatted final tweet
        """
        # Get random hashtags
        all_hashtags = self.tweet_style.get('hashtags', ['#Tech', '#AI'])
        max_hashtags = self.tweet_style.get('max_hashtags', 2)
        selected_hashtags = random.sample(all_hashtags, min(max_hashtags, len(all_hashtags)))
        hashtags_str = ' '.join(selected_hashtags)
        
        # Build full tweet
        full_tweet = f"{content} {hashtags_str} {article_link}"
        
        return full_tweet


if __name__ == "__main__":
    # Test the tweet generator
    import os
    from dotenv import load_dotenv
    
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        exit(1)
    
    generator = TweetGenerator(api_key)
    
    # Test article
    test_article = {
        'title': 'OpenAI Announces GPT-5 with Revolutionary Reasoning Capabilities',
        'summary': 'OpenAI has unveiled GPT-5, featuring advanced reasoning abilities that can solve complex mathematical problems and understand nuanced context better than ever before.',
        'link': 'https://example.com/gpt5-announcement'
    }
    
    print("\n🤖 Generating tweet...\n")
    content = generator.generate_tweet(test_article)
    
    if content:
        full_tweet = generator.format_final_tweet(content, test_article['link'])
        print(f"✅ Generated Tweet ({len(full_tweet)} chars):")
        print(f"\n{full_tweet}\n")
    else:
        print("❌ Failed to generate tweet")
