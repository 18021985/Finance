import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    ITICK_API_KEY = os.getenv("ITICK_API_KEY", "")
    INDIAN_API_KEY = os.getenv("INDIAN_API_KEY", "")
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
    EIA_API_KEY = os.getenv("EIA_API_KEY", "")
    FRED_API_KEY = os.getenv("FRED_API_KEY", "")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Log API key configuration
    logger = __import__('logging').getLogger(__name__)
    logger.info(f"ALPHA_VANTAGE_API_KEY configured: {bool(ALPHA_VANTAGE_API_KEY)}")
    logger.info(f"NEWS_API_KEY configured: {bool(NEWS_API_KEY)}")
    logger.info(f"ITICK_API_KEY configured: {bool(ITICK_API_KEY)}")
    logger.info(f"INDIAN_API_KEY configured: {bool(INDIAN_API_KEY)}")
    logger.info(f"FINNHUB_API_KEY configured: {bool(FINNHUB_API_KEY)}")
    logger.info(f"EIA_API_KEY configured: {bool(EIA_API_KEY)}")
    logger.info(f"FRED_API_KEY configured: {bool(FRED_API_KEY)}")
    
    # Rate limiting for free APIs
    ALPHA_VANTAGE_RATE_LIMIT = 5  # requests per minute
    NEWS_API_RATE_LIMIT = 100  # requests per day
    
    # Cache duration in seconds
    CACHE_DURATION = 300  # 5 minutes

config = Config()

# Log API key status for debugging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"ALPHA_VANTAGE_API_KEY configured: {bool(config.ALPHA_VANTAGE_API_KEY)}")
logger.info(f"NEWS_API_KEY configured: {bool(config.NEWS_API_KEY)}")
logger.info(f"ITICK_API_KEY configured: {bool(config.ITICK_API_KEY)}")
logger.info(f"FINNHUB_API_KEY configured: {bool(config.FINNHUB_API_KEY)}")
logger.info(f"EIA_API_KEY configured: {bool(config.EIA_API_KEY)}")
logger.info(f"FRED_API_KEY configured: {bool(config.FRED_API_KEY)}")
