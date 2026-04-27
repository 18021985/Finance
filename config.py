import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    ITICK_API_KEY = os.getenv("ITICK_API_KEY", "")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
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
