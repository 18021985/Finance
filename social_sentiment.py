import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import re

# Try to import social media APIs
try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    print("Tweepy not available. Install with: pip install tweepy")

try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False
    print("PRAW not available. Install with: pip install praw")

from textblob import TextBlob

@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    source: str
    symbol: str
    sentiment_score: float  # -1 to 1
    sentiment_label: str  # 'positive', 'negative', 'neutral'
    confidence: float
    mentions: int
    timestamp: datetime
    sample_posts: List[str]

class SocialSentimentAnalyzer:
    """
    Social sentiment analysis from Twitter and Reddit
    
    Features:
    - Twitter sentiment analysis
    - Reddit sentiment analysis
    - Sentiment aggregation
    - Trend analysis
    """
    
    def __init__(self, twitter_api_key: str = None, reddit_client_id: str = None,
                 reddit_client_secret: str = None):
        self.twitter_api_key = twitter_api_key
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret
        
        # Initialize clients if credentials provided
        self.twitter_client = None
        self.reddit_client = None
        
        if TWITTER_AVAILABLE and twitter_api_key:
            self._init_twitter()
        
        if REDDIT_AVAILABLE and reddit_client_id:
            self._init_reddit()
    
    def _init_twitter(self):
        """Initialize Twitter client"""
        try:
            auth = tweepy.OAuthHandler(self.twitter_api_key, self.twitter_api_secret)
            self.twitter_client = tweepy.API(auth)
            print("Twitter client initialized")
        except Exception as e:
            print(f"Error initializing Twitter: {e}")
    
    def _init_reddit(self):
        """Initialize Reddit client"""
        try:
            self.reddit_client = praw.Reddit(
                client_id=self.reddit_client_id,
                client_secret=self.reddit_client_secret,
                user_agent='FinancialIntelligence/1.0'
            )
            print("Reddit client initialized")
        except Exception as e:
            print(f"Error initializing Reddit: {e}")
    
    def analyze_text_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text using TextBlob
        
        Args:
            text: Text to analyze
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.1:
            label = 'positive'
        elif polarity < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'label': label
        }
    
    def get_twitter_sentiment(self, symbol: str, days: int = 1, 
                            limit: int = 100) -> SentimentResult:
        """
        Get sentiment from Twitter
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            days: Number of days to look back
            limit: Number of tweets to analyze
        """
        if not TWITTER_AVAILABLE or self.twitter_client is None:
            return SentimentResult(
                source='twitter',
                symbol=symbol,
                sentiment_score=0.0,
                sentiment_label='neutral',
                confidence=0.0,
                mentions=0,
                timestamp=datetime.now(),
                sample_posts=[]
            )
        
        try:
            # Search for tweets
            query = f"${symbol} OR {symbol} stock"
            tweets = self.twitter_client.search_tweets(q=query, count=limit, lang='en')
            
            if not tweets:
                return SentimentResult(
                    source='twitter',
                    symbol=symbol,
                    sentiment_score=0.0,
                    sentiment_label='neutral',
                    confidence=0.0,
                    mentions=0,
                    timestamp=datetime.now(),
                    sample_posts=[]
                )
            
            # Analyze sentiment
            sentiments = []
            sample_posts = []
            
            for tweet in tweets:
                text = tweet.text
                sentiment = self.analyze_text_sentiment(text)
                sentiments.append(sentiment['polarity'])
                
                if len(sample_posts) < 5:
                    sample_posts.append(text)
            
            # Calculate aggregate sentiment
            avg_sentiment = np.mean(sentiments) if sentiments else 0
            std_sentiment = np.std(sentiments) if sentiments else 0
            
            if avg_sentiment > 0.1:
                label = 'positive'
            elif avg_sentiment < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            # Confidence based on standard deviation
            confidence = 1 - min(std_sentiment, 1.0)
            
            return SentimentResult(
                source='twitter',
                symbol=symbol,
                sentiment_score=round(avg_sentiment, 3),
                sentiment_label=label,
                confidence=round(confidence, 3),
                mentions=len(tweets),
                timestamp=datetime.now(),
                sample_posts=sample_posts
            )
        except Exception as e:
            print(f"Error getting Twitter sentiment: {e}")
            return SentimentResult(
                source='twitter',
                symbol=symbol,
                sentiment_score=0.0,
                sentiment_label='neutral',
                confidence=0.0,
                mentions=0,
                timestamp=datetime.now(),
                sample_posts=[]
            )
    
    def get_reddit_sentiment(self, symbol: str, subreddit: str = 'wallstreetbets',
                           limit: int = 100) -> SentimentResult:
        """
        Get sentiment from Reddit
        
        Args:
            symbol: Stock ticker
            subreddit: Subreddit to search
            limit: Number of posts to analyze
        """
        if not REDDIT_AVAILABLE or self.reddit_client is None:
            return SentimentResult(
                source='reddit',
                symbol=symbol,
                sentiment_score=0.0,
                sentiment_label='neutral',
                confidence=0.0,
                mentions=0,
                timestamp=datetime.now(),
                sample_posts=[]
            )
        
        try:
            # Search subreddit
            subreddit_obj = self.reddit_client.subreddit(subreddit)
            posts = subreddit_obj.search(symbol, limit=limit)
            
            if not posts:
                return SentimentResult(
                    source='reddit',
                    symbol=symbol,
                    sentiment_score=0.0,
                    sentiment_label='neutral',
                    confidence=0.0,
                    mentions=0,
                    timestamp=datetime.now(),
                    sample_posts=[]
                )
            
            # Analyze sentiment
            sentiments = []
            sample_posts = []
            
            for post in posts:
                text = post.title + ' ' + post.selftext
                sentiment = self.analyze_text_sentiment(text)
                sentiments.append(sentiment['polarity'])
                
                if len(sample_posts) < 5:
                    sample_posts.append(post.title)
            
            # Calculate aggregate sentiment
            avg_sentiment = np.mean(sentiments) if sentiments else 0
            std_sentiment = np.std(sentiments) if sentiments else 0
            
            if avg_sentiment > 0.1:
                label = 'positive'
            elif avg_sentiment < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            confidence = 1 - min(std_sentiment, 1.0)
            
            return SentimentResult(
                source='reddit',
                symbol=symbol,
                sentiment_score=round(avg_sentiment, 3),
                sentiment_label=label,
                confidence=round(confidence, 3),
                mentions=len(list(posts)),
                timestamp=datetime.now(),
                sample_posts=sample_posts
            )
        except Exception as e:
            print(f"Error getting Reddit sentiment: {e}")
            return SentimentResult(
                source='reddit',
                symbol=symbol,
                sentiment_score=0.0,
                sentiment_label='neutral',
                confidence=0.0,
                mentions=0,
                timestamp=datetime.now(),
                sample_posts=[]
            )
    
    def get_aggregated_sentiment(self, symbol: str) -> Dict:
        """
        Get aggregated sentiment from all sources
        
        Args:
            symbol: Stock ticker
        """
        results = []
        
        # Twitter sentiment
        twitter_result = self.get_twitter_sentiment(symbol)
        results.append(twitter_result)
        
        # Reddit sentiment (multiple subreddits)
        subreddits = ['wallstreetbets', 'stocks', 'investing']
        for subreddit in subreddits:
            reddit_result = self.get_reddit_sentiment(symbol, subreddit)
            results.append(reddit_result)
        
        # Calculate weighted average
        weighted_score = 0
        total_weight = 0
        
        for result in results:
            if result.mentions > 0:
                weight = result.mentions
                weighted_score += result.sentiment_score * weight
                total_weight += weight
        
        if total_weight > 0:
            avg_score = weighted_score / total_weight
        else:
            avg_score = 0
        
        if avg_score > 0.1:
            overall_label = 'positive'
        elif avg_score < -0.1:
            overall_label = 'negative'
        else:
            overall_label = 'neutral'
        
        return {
            'symbol': symbol,
            'overall_sentiment': round(avg_score, 3),
            'overall_label': overall_label,
            'sources': [
                {
                    'source': r.source,
                    'sentiment': r.sentiment_score,
                    'label': r.sentiment_label,
                    'mentions': r.mentions
                }
                for r in results
            ],
            'timestamp': datetime.now()
        }
    
    def get_sentiment_trend(self, symbol: str, days: int = 7) -> Dict:
        """
        Get sentiment trend over time
        
        Args:
            symbol: Stock ticker
            days: Number of days to analyze
        """
        # This would require historical data storage
        # For now, return placeholder
        return {
            'symbol': symbol,
            'trend': 'neutral',
            'change': 0.0,
            'period_days': days,
            'note': 'Historical sentiment tracking requires database implementation'
        }
