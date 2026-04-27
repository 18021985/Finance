"""
Alpha Vantage News & Sentiment API Provider
Fetches market news with sentiment analysis and stock impact indicators
"""
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)


class AlphaVantageNewsProvider:
    """Fetch news from Alpha Vantage NEWS_SENTIMENT API"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.ALPHA_VANTAGE_API_KEY
        
    def get_news(self, tickers: Optional[str] = None, topics: Optional[str] = None, 
                 limit: int = 20, time_from: Optional[str] = None) -> List[Dict]:
        """
        Fetch news with sentiment analysis
        
        Args:
            tickers: Comma-separated stock symbols (e.g., "AAPL" or "COIN,CRYPTO:BTC")
            topics: Comma-separated topics (e.g., "technology,earnings")
            limit: Number of articles to return (max 1000)
            time_from: Start time in YYYYMMDDTHHMM format
            
        Returns:
            List of news articles with sentiment data
        """
        if not self.api_key:
            logger.warning("Alpha Vantage API key not configured")
            return []
        
        params = {
            "function": "NEWS_SENTIMENT",
            "apikey": self.api_key,
            "limit": min(limit, 1000)
        }
        
        if tickers:
            params["tickers"] = tickers
        if topics:
            params["topics"] = topics
        if time_from:
            params["time_from"] = time_from
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "feed" not in data:
                logger.warning(f"No news data returned: {data.get('Note', 'Unknown error')}")
                return []
            
            articles = []
            for item in data["feed"][:limit]:
                # Extract ticker sentiment scores
                ticker_sentiment = {}
                for ticker_data in item.get("ticker_sentiment", []):
                    ticker_sentiment[ticker_data["ticker"]] = {
                        "relevance_score": float(ticker_data.get("relevance_score", 0)),
                        "ticker_sentiment_score": float(ticker_data.get("ticker_sentiment_score", 0)),
                        "ticker_sentiment_label": ticker_data.get("ticker_sentiment_label", "neutral")
                    }
                
                # Extract overall sentiment
                overall_sentiment = item.get("overall_sentiment_score", 0)
                sentiment_label = item.get("overall_sentiment_label", "neutral")
                
                articles.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "time_published": item.get("time_published", ""),
                    "authors": item.get("authors", []),
                    "summary": item.get("summary", ""),
                    "source": item.get("source", ""),
                    "topics": [
                        {
                            "topic": t.get("topic", ""),
                            "relevance_score": float(t.get("relevance_score", 0))
                        }
                        for t in item.get("topics", [])
                    ],
                    "overall_sentiment_score": float(overall_sentiment) if overall_sentiment else 0.0,
                    "overall_sentiment_label": sentiment_label,
                    "ticker_sentiment": ticker_sentiment,
                    "market_impact": self._assess_market_impact(overall_sentiment, ticker_sentiment)
                })
            
            return articles
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Alpha Vantage news: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing Alpha Vantage news: {e}")
            return []
    
    def _assess_market_impact(self, overall_sentiment: float, 
                            ticker_sentiment: Dict[str, Dict]) -> str:
        """
        Assess potential market impact based on sentiment scores
        
        Args:
            overall_sentiment: Overall sentiment score (-1 to 1)
            ticker_sentiment: Per-ticker sentiment scores
            
        Returns:
            Impact level: "high_positive", "moderate_positive", "neutral", 
                         "moderate_negative", "high_negative"
        """
        if not ticker_sentiment:
            # Use overall sentiment if no ticker-specific data
            if overall_sentiment >= 0.3:
                return "moderate_positive"
            elif overall_sentiment <= -0.3:
                return "moderate_negative"
            return "neutral"
        
        # Calculate average ticker sentiment
        avg_ticker_sentiment = sum(
            t["ticker_sentiment_score"] for t in ticker_sentiment.values()
        ) / len(ticker_sentiment)
        
        # Determine impact based on sentiment strength
        if avg_ticker_sentiment >= 0.5:
            return "high_positive"
        elif avg_ticker_sentiment >= 0.2:
            return "moderate_positive"
        elif avg_ticker_sentiment <= -0.5:
            return "high_negative"
        elif avg_ticker_sentiment <= -0.2:
            return "moderate_negative"
        return "neutral"
    
    def get_news_for_symbol(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get news specifically for a stock symbol
        
        Args:
            symbol: Stock ticker symbol
            limit: Number of articles to return
            
        Returns:
            List of news articles for the symbol
        """
        return self.get_news(tickers=symbol, limit=limit)
    
    def get_market_news(self, topics: str = "financial_markets,economy_macro", 
                       limit: int = 20) -> List[Dict]:
        """
        Get general market news
        
        Args:
            topics: News topics to filter
            limit: Number of articles to return
            
        Returns:
            List of market news articles
        """
        return self.get_news(topics=topics, limit=limit)
