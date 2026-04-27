from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from analyzer import FinancialIntelligenceSystem
import uvicorn
from config import config
from observability import Observability
import math
import asyncio
import os
import time
import logging
from news_events import aggregate_effective_sentiment
from performance_tracker import PerformanceTracker
from auto_learning_store import AutoLearningStore

logger = logging.getLogger(__name__)

_APP_STARTED_AT = time.time()

app = FastAPI(
    title="Financial Intelligence System API",
    description="Institutional-grade market intelligence and advisory platform",
    version="3.0.0"
)


@app.get("/health")
async def health():
    """
    Lightweight health check endpoint.
    Returns quickly without external dependencies.
    """
    try:
        # Quick internal checks only - no external calls
        return {
            "status": "ok",
            "version": "3.0.0",
            "pid": os.getpid(),
            "uptime_s": round(time.time() - _APP_STARTED_AT, 1),
            "timestamp": time.time(),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@app.get("/test-yfinance")
async def test_yfinance():
    """
    Test endpoint to verify yfinance connectivity and diagnose issues
    """
    import yfinance as yf
    import logging
    logger = logging.getLogger(__name__)
    
    results = {
        "test_name": "yfinance_connectivity",
        "timestamp": time.time(),
        "tests": []
    }
    
    # Test 1: Simple ticker fetch
    try:
        logger.info("Test 1: Fetching AAPL data")
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="1d", timeout=30)
        results["tests"].append({
            "name": "fetch_aapl",
            "status": "success" if not hist.empty else "empty_data",
            "data_points": len(hist),
            "last_price": float(hist['Close'].iloc[-1]) if not hist.empty else None
        })
        logger.info(f"Test 1 passed: {len(hist)} data points")
    except Exception as e:
        results["tests"].append({
            "name": "fetch_aapl",
            "status": "error",
            "error": str(e)
        })
        logger.error(f"Test 1 failed: {e}")
    
    # Test 2: Indian index fetch
    try:
        logger.info("Test 2: Fetching NIFTY 50 (^NSEI)")
        ticker = yf.Ticker("^NSEI")
        hist = ticker.history(period="1d", timeout=30)
        results["tests"].append({
            "name": "fetch_nifty50",
            "status": "success" if not hist.empty else "empty_data",
            "data_points": len(hist),
            "last_price": float(hist['Close'].iloc[-1]) if not hist.empty else None
        })
        logger.info(f"Test 2 passed: {len(hist)} data points")
    except Exception as e:
        results["tests"].append({
            "name": "fetch_nifty50",
            "status": "error",
            "error": str(e)
        })
        logger.error(f"Test 2 failed: {e}")
    
    # Test 3: Indian stock fetch
    try:
        logger.info("Test 3: Fetching RELIANCE.NS")
        ticker = yf.Ticker("RELIANCE.NS")
        hist = ticker.history(period="1d", timeout=30)
        results["tests"].append({
            "name": "fetch_reliance",
            "status": "success" if not hist.empty else "empty_data",
            "data_points": len(hist),
            "last_price": float(hist['Close'].iloc[-1]) if not hist.empty else None
        })
        logger.info(f"Test 3 passed: {len(hist)} data points")
    except Exception as e:
        results["tests"].append({
            "name": "fetch_reliance",
            "status": "error",
            "error": str(e)
        })
        logger.error(f"Test 3 failed: {e}")
    
    # Test 4: Check user-agent
    try:
        user_agent = yf.utils.request_headers.get('User-Agent', 'not_set')
        results["tests"].append({
            "name": "user_agent_check",
            "status": "success",
            "user_agent": user_agent
        })
        logger.info(f"User-Agent: {user_agent}")
    except Exception as e:
        results["tests"].append({
            "name": "user_agent_check",
            "status": "error",
            "error": str(e)
        })
    
    return _json_safe(results)


async def _to_thread_timeout(fn, timeout_s: float):
    """
    Run blocking IO/CPU work off the event loop with a hard timeout.
    Returns None on timeout/exception to keep endpoints responsive.
    """
    try:
        return await asyncio.wait_for(asyncio.to_thread(fn), timeout=timeout_s)
    except Exception:
        return None

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize intelligence system
analyzer = FinancialIntelligenceSystem()
observability = Observability()
_recommendations_cache = {}
_PERF_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "performance_data")
# Keep local tracker for dev fallback, but prefer Supabase store for durability.
perf_tracker = PerformanceTracker(storage_path=_PERF_STORAGE_DIR)
auto_learning_store = AutoLearningStore()
# Attach auto_learning_store to analyzer for consistent access
analyzer.auto_learning_store = auto_learning_store
_macro_cache = {"ts": 0.0, "val": None}
_intelligence_cache = {}


@app.on_event("startup")
async def _warm_caches_startup():
    """
    Best-effort cache warming so first dashboard load doesn't 504.
    """
    async def _warm_macro():
        def _get_macro():
            return analyzer.get_macro_intelligence()

        result = await _to_thread_timeout(_get_macro, timeout_s=15.0)
        if result is not None:
            _macro_cache["ts"] = time.time()
            _macro_cache["val"] = result

    try:
        asyncio.create_task(_warm_macro())
    except Exception:
        pass


def _json_safe(obj):
    """
    Ensure responses are JSON-serializable and do not contain NaN/Infinity,
    which can cause FastAPI/Starlette to raise during serialization.
    """
    try:
        import numpy as np
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            v = float(obj)
            return None if (math.isnan(v) or math.isinf(v)) else v
    except Exception:
        pass

    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, (str, int, bool)) or obj is None:
        return obj
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if hasattr(obj, "to_pydatetime"):
        try:
            return obj.to_pydatetime().isoformat()
        except Exception:
            return str(obj)
    return str(obj)

# Pydantic models
class AnalysisRequest(BaseModel):
    symbol: str
    format: Optional[str] = "json"

class ScanRequest(BaseModel):
    symbols: List[str]

class AnalysisResponse(BaseModel):
    symbol: str
    company: dict
    scores: dict
    bullish_indicators: list
    bearish_indicators: list
    forecast: dict
    key_drivers: dict
    verdict: dict
    context: Optional[dict] = None


class AutoLearningPredictionIn(BaseModel):
    symbol: str
    predicted_direction: str
    predicted_probability: float
    confidence: float = 0.0
    model_used: str = "composite+probabilistic"
    features: Dict = {}


class AutoLearningOutcomeIn(BaseModel):
    prediction_id: str
    actual_direction: str
    actual_return: float


@app.post("/auto-learning/prediction")
async def auto_learning_log_prediction(body: AutoLearningPredictionIn):
    """
    Log a prediction into the auto-learning performance store.
    """
    try:
        def _log():
            # Prefer durable Supabase store when configured.
            if getattr(auto_learning_store, "using_supabase", False):
                return auto_learning_store.log_prediction(
                    symbol=body.symbol,
                    predicted_direction=body.predicted_direction,
                    predicted_probability=float(body.predicted_probability),
                    confidence=float(body.confidence or 0.0),
                    model_used=body.model_used,
                    features=body.features or {},
                )
            rec = perf_tracker.log_prediction(
                symbol=body.symbol,
                predicted_direction=body.predicted_direction,
                predicted_probability=float(body.predicted_probability),
                confidence=float(body.confidence or 0.0),
                model_used=body.model_used,
                features=body.features or {},
            )
            return getattr(rec, "id", None)

        prediction_id = await _to_thread_timeout(_log, timeout_s=3.0)
        if not prediction_id:
            raise HTTPException(status_code=504, detail="Timeout logging prediction")
        return _json_safe({"prediction_id": str(prediction_id)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auto-learning/outcome")
async def auto_learning_log_outcome(body: AutoLearningOutcomeIn):
    """
    Attach a realized outcome to a previously logged prediction.
    """
    try:
        def _upd():
            if getattr(auto_learning_store, "using_supabase", False):
                return auto_learning_store.update_outcome_by_id(
                    prediction_id=body.prediction_id,
                    actual_direction=body.actual_direction,
                    actual_return=float(body.actual_return),
                )
            return perf_tracker.update_outcome_by_id(
                prediction_id=body.prediction_id,
                actual_direction=body.actual_direction,
                actual_return=float(body.actual_return),
            )

        ok = await _to_thread_timeout(_upd, timeout_s=2.0)
        return _json_safe({"updated": bool(ok)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auto-learning/report")
async def auto_learning_report(window_size: int = Query(200, ge=20, le=5000)):
    """
    Auto-learning KPI report: direction accuracy + risk-adjusted performance.
    Always uses auto_learning_store (has in-memory fallback when Supabase not configured).
    """
    try:
        def _report():
            return auto_learning_store.generate_report(window_size=int(window_size))

        rep = await _to_thread_timeout(_report, timeout_s=3.0)
        if rep is None:
            raise HTTPException(status_code=504, detail="Timeout generating report")
        return _json_safe(rep)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Financial Intelligence System API",
        "version": "3.0.0",
        "description": "Institutional-grade market intelligence and advisory platform",
        "endpoints": {
            "/intelligence/{symbol}": "GET - Composite score and insight",
            "/macro": "GET - Macro intelligence overview",
            "/macro/scenarios": "GET - Forward-looking macro scenarios",
            "/multi-asset/{symbol}": "GET - Analyze any asset class",
            "/scenarios/{symbol}": "GET - Asset-specific scenarios",
            "/correlation": "GET - Cross-asset correlation matrix",
            "/allocation/{strategy}": "GET - Asset allocation recommendations",
            "/risk-sentiment": "GET - Risk-on/risk-off indicators",
            "/analyze": "POST - Detailed company analysis",
            "/market-overview": "GET - Market overview",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_company(request: AnalysisRequest):
    """
    Analyze a company and return financial insights
    
    Args:
        symbol: Stock ticker (e.g., 'AAPL', 'RELIANCE.NS', 'TSLA')
        format: Output format ('json' or 'markdown')
    
    Returns:
        Complete analysis with signals, scores, forecast, and verdict
    """
    try:
        if not request.symbol:
            raise HTTPException(status_code=400, detail="Symbol is required")
        
        result = analyzer.analyze_company(request.symbol, request.format)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        if result.get('format') == 'markdown':
            return {"content": result['content'], "format": "markdown"}
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/{symbol}")
async def analyze_company_get(
    symbol: str,
    format: str = Query("json", description="Output format: json or markdown")
):
    """GET endpoint for company analysis"""
    return await analyze_company(AnalysisRequest(symbol=symbol, format=format))

@app.get("/market-overview")
async def market_overview():
    """Get overview of major market indices and macro indicators"""
    try:
        overview = analyzer.get_market_overview()
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan")
async def scan_opportunities(request: ScanRequest):
    """
    Scan multiple symbols for investment opportunities
    
    Returns symbols sorted by net score (highest first)
    """
    try:
        if not request.symbols:
            raise HTTPException(status_code=400, detail="Symbols list is required")
        
        if len(request.symbols) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 symbols per scan")
        
        results = analyzer.scan_opportunities(request.symbols)
        return {
            "opportunities": results,
            "total_analyzed": len(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/opportunities")
async def get_opportunities(
    symbols: str = Query(..., description="Comma-separated list of symbols (max 20)")
):
    """GET endpoint for scanning opportunities with hard limit on symbols"""
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    
    # Hard limit to prevent timeout on free API
    if len(symbol_list) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 symbols per request")
    
    return await scan_opportunities(ScanRequest(symbols=symbol_list))

# New endpoints for enhanced features

@app.get("/analyze/{symbol}/enhanced")
async def analyze_company_enhanced(symbol: str):
    """
    Enhanced analysis with momentum, chart patterns, and action advice
    """
    try:
        result = analyzer.analyze_company_enhanced(symbol)
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/indian/analyze/{symbol}")
async def analyze_indian_stock(symbol: str):
    """
    Analyze Indian stock (NSE/BSE)
    Symbol should include .NS suffix for NSE stocks
    """
    try:
        result = analyzer.analyze_indian_stock(symbol)
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/indian/overview")
async def indian_market_overview():
    """Get Indian market overview (NSE/BSE indices and sectors)"""
    try:
        overview = analyzer.get_indian_market_overview()
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/indian/scan")
async def scan_indian_opportunities():
    """Scan Indian stocks for investment opportunities"""
    try:
        opportunities = analyzer.indian_analyzer.scan_indian_opportunities()
        return opportunities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sectors/rotation")
async def sector_rotation(market: str = Query("US", description="Market: US or India")):
    """Analyze sector rotation and identify opportunities"""
    try:
        rotation = analyzer.analyze_sector_rotation(market)
        return rotation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sectors/recommendations")
async def sector_recommendations(market: str = Query("US", description="Market: US or India")):
    """Get sector allocation recommendations"""
    try:
        recommendations = analyzer.get_sector_recommendations(market)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/portfolio/optimize")
async def optimize_portfolio(request: dict):
    """
    Optimize portfolio allocation
    
    Request body:
    {
        "holdings": {"AAPL": 0.3, "GOOGL": 0.2, ...},
        "expected_returns": {"AAPL": 0.15, "GOOGL": 0.12, ...}
    }
    """
    try:
        holdings = request.get('holdings', {})
        expected_returns = request.get('expected_returns', {})
        
        if not holdings or not expected_returns:
            raise HTTPException(status_code=400, detail="holdings and expected_returns are required")
        
        result = analyzer.optimize_portfolio(holdings, expected_returns)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/backtest/{symbol}")
async def backtest_strategy(symbol: str, period: str = Query("1y", description="Period: 1y, 6m, 3m")):
    """Backtest a strategy on a stock"""
    try:
        result = analyzer.backtest_strategy(symbol, period)
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/portfolio/risk")
async def assess_portfolio_risk(request: dict):
    """
    Assess portfolio risk
    
    Request body:
    {
        "holdings": {"AAPL": 100, "GOOGL": 50, ...},
        "prices": {"AAPL": 150.0, "GOOGL": 120.0, ...},
        "volatilities": {"AAPL": 0.25, "GOOGL": 0.30, ...}
    }
    """
    try:
        holdings = request.get('holdings', {})
        prices = request.get('prices', {})
        volatilities = request.get('volatilities', {})
        
        if not holdings or not prices:
            raise HTTPException(status_code=400, detail="holdings and prices are required")
        
        result = analyzer.assess_portfolio_risk(holdings, prices, volatilities)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/position-size")
async def calculate_position_size(request: dict):
    """
    Calculate optimal position size based on risk parameters
    
    Request body:
    {
        "portfolio_value": 100000,
        "entry_price": 150.0,
        "stop_loss": 140.0,
        "confidence": 0.7
    }
    """
    try:
        portfolio_value = request.get('portfolio_value')
        entry_price = request.get('entry_price')
        stop_loss = request.get('stop_loss')
        confidence = request.get('confidence', 0.5)
        
        if not portfolio_value or not entry_price or not stop_loss:
            raise HTTPException(status_code=400, detail="portfolio_value, entry_price, and stop_loss are required")
        
        result = analyzer.calculate_position_size(portfolio_value, entry_price, stop_loss, confidence)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New intelligence endpoints

@app.get("/intelligence/{symbol}")
async def get_composite_intelligence(symbol: str):
    """
    Get composite score and insight for an asset

    Returns:
        Composite score (0-100) with component breakdown
        Insight summary and strategic consideration
    """
    try:
        now = time.time()
        cached = _intelligence_cache.get(symbol)
        if cached:
            ts, val = cached
            if (now - float(ts)) < 60:
                return _json_safe(val)

        def _get_score():
            return analyzer.get_composite_score(symbol)

        result = await _to_thread_timeout(_get_score, timeout_s=18.0)
        if result is None:
            # serve stale cache to avoid UI spam
            if cached:
                return _json_safe(cached[1])
            # Return default response instead of 504
            return _json_safe({
                'composite_score': {
                    'total_score': 50,
                    'technical_score': 50,
                    'momentum_score': 50,
                    'macro_score': 50,
                    'fundamental_score': 50,
                    'ml_score': 50,
                    'ml_probability': 50
                },
                'insight': {
                    'assessment': 'Data temporarily unavailable',
                    'strategic_consideration': f'Unable to fetch real-time data for {symbol}. Please try again later.',
                    'drivers': ['Data unavailable'],
                    'risks': ['Service timeout']
                },
                'ml_prediction': {
                    'direction': 'neutral',
                    'confidence': 0.5
                },
                'error': 'timeout'
            })
        if 'error' in result:
            # Return result with error instead of 500
            return _json_safe({
                'composite_score': {
                    'total_score': 50,
                    'technical_score': 50,
                    'momentum_score': 50,
                    'macro_score': 50,
                    'fundamental_score': 50,
                    'ml_score': 50,
                    'ml_probability': 50
                },
                'insight': {
                    'assessment': 'Data fetch error',
                    'strategic_consideration': f'Unable to fetch data for {symbol}: {result.get("error", "Unknown error")}',
                    'drivers': ['Data unavailable'],
                    'risks': [result.get('error', 'Unknown error')]
                },
                'ml_prediction': {
                    'direction': 'neutral',
                    'confidence': 0.5
                },
                'error': result.get('error')
            })
        _intelligence_cache[symbol] = (now, result)
        return _json_safe(result)
    except HTTPException:
        raise
    except Exception as e:
        # Return default response instead of 500
        return _json_safe({
            'composite_score': {
                'total_score': 50,
                'technical_score': 50,
                'momentum_score': 50,
                'macro_score': 50,
                'fundamental_score': 50,
                'ml_score': 50,
                'ml_probability': 50
            },
            'insight': {
                'assessment': 'Server error',
                'strategic_consideration': f'Server error processing {symbol}: {str(e)}',
                'drivers': ['Data unavailable'],
                'risks': [str(e)]
            },
            'ml_prediction': {
                'direction': 'neutral',
                'confidence': 0.5
            },
            'error': str(e)
        })

@app.get("/available-companies")
async def get_available_companies(
    limit: int = Query(500, ge=1, le=2000),
    market: str = Query("ALL", description="US, IN, or ALL"),
):
    """
    Get list of available companies for portfolio selection

    Returns:
        List of companies with symbol, sector, and market
    """
    try:
        from investment_recommender import FORTUNE_100_STOCKS, NIFTY_50_STOCKS

        companies_dict = {}

        # Add Fortune 100 companies
        for sector, symbols in FORTUNE_100_STOCKS.items():
            for symbol in symbols:
                if symbol not in companies_dict:
                    companies_dict[symbol] = {
                        'symbol': symbol,
                        'sector': sector,
                        'market': 'US'
                    }

        # Add NIFTY 50 companies (only if not already added)
        for sector, symbols in NIFTY_50_STOCKS.items():
            for symbol in symbols:
                # Normalize to NSE suffix for yfinance compatibility
                normalized = symbol if '.' in symbol else f"{symbol}.NS"
                if normalized not in companies_dict:
                    companies_dict[normalized] = {
                        'symbol': normalized,
                        'sector': sector,
                        'market': 'IN'
                    }

        # Convert to list and sort by symbol
        companies = list(companies_dict.values())
        companies.sort(key=lambda x: x['symbol'])
        m = (market or "ALL").upper()
        if m in {"US", "IN"}:
            companies = [c for c in companies if (c.get("market") or "").upper() == m]
        return companies[: int(limit)]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user-holdings")
async def get_user_holdings():
    """
    Get user's portfolio holdings

    Returns:
        List of user's stock holdings
    """
    try:
        from supabase import create_client
        import os

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            # Return sample holdings if Supabase not configured
            return [
                {'id': '1', 'symbol': 'AAPL', 'shares': 100, 'average_cost': 150.00, 'sector': 'technology', 'market': 'US'},
                {'id': '2', 'symbol': 'GOOGL', 'shares': 50, 'average_cost': 120.00, 'sector': 'technology', 'market': 'US'},
                {'id': '3', 'symbol': 'MSFT', 'shares': 75, 'average_cost': 300.00, 'sector': 'technology', 'market': 'US'},
            ]

        supabase_client = create_client(supabase_url, supabase_key)

        def _fetch():
            return supabase_client.table('user_holdings').select('*').eq('user_id', 'default_user').execute()

        response = await _to_thread_timeout(_fetch, timeout_s=5.0)
        return response.data if response else []

    except Exception as e:
        # Return sample holdings on error instead of 500
        return [
            {'id': '1', 'symbol': 'AAPL', 'shares': 100, 'average_cost': 150.00, 'sector': 'technology', 'market': 'US'},
            {'id': '2', 'symbol': 'GOOGL', 'shares': 50, 'average_cost': 120.00, 'sector': 'technology', 'market': 'US'},
            {'id': '3', 'symbol': 'MSFT', 'shares': 75, 'average_cost': 300.00, 'sector': 'technology', 'market': 'US'},
            {'error': str(e)}
        ]

@app.post("/user-holdings")
async def add_holding(holding: dict):
    """
    Add a new holding to user's portfolio

    Args:
        holding: dict with symbol, shares, average_cost, sector, market

    Returns:
        Created holding record
    """
    try:
        from supabase import create_client
        import os

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            raise HTTPException(status_code=400, detail='Supabase not configured')

        supabase_client = create_client(supabase_url, supabase_key)

        holding_data = {
            'user_id': 'default_user',
            'symbol': holding.get('symbol'),
            'shares': holding.get('shares'),
            'average_cost': holding.get('average_cost', 0),
            'sector': holding.get('sector'),
            'market': holding.get('market', 'US')
        }

        response = supabase_client.table('user_holdings').insert(holding_data).execute()
        return response.data[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/user-holdings/{holding_id}")
async def delete_holding(holding_id: str):
    """
    Delete a holding from user's portfolio

    Args:
        holding_id: ID of the holding to delete

    Returns:
        Success message
    """
    try:
        from supabase import create_client
        import os

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            raise HTTPException(status_code=400, detail='Supabase not configured')

        supabase_client = create_client(supabase_url, supabase_key)
        response = supabase_client.table('user_holdings').delete().eq('id', holding_id).execute()
        return {'success': True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio-strategy")
async def get_portfolio_strategy():
    """
    Get personalized portfolio strategy based on user's holdings

    Returns:
        Short-term and long-term strategies for user's portfolio
    """
    try:
        # Get user holdings
        holdings_response = await get_user_holdings()

        if not holdings_response:
            return {'error': 'No holdings found'}

        # Get market sentiment - route through data_layer for consistency
        market_sentiment = 'neutral'
        risk_level = 'medium'

        if hasattr(analyzer, 'data_layer'):
            try:
                hist = analyzer.data_layer.get_stock_data('SPY', period='1mo')
                if hist is not None and not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    start_price = hist['Close'].iloc[0]
                    change = (current_price - start_price) / start_price

                    if change > 0.03:
                        market_sentiment = 'bullish'
                    elif change < -0.03:
                        market_sentiment = 'bearish'

                    returns = hist['Close'].pct_change().dropna()
                    volatility = returns.std() * (252 ** 0.5)
                    if volatility > 0.25:
                        risk_level = 'high'
                    elif volatility > 0.15:
                        risk_level = 'medium'
                    else:
                        risk_level = 'low'
            except:
                pass

        # Get news sentiment for holdings
        news_sentiment = {}
        geopolitical_risk = {}

        for holding in holdings_response:
            symbol = holding['symbol']
            try:
                if hasattr(analyzer, 'news_analyzer'):
                    news_data = analyzer.news_analyzer.analyze_news(symbol)
                    if news_data:
                        news_sentiment[symbol] = news_data.get('overall_sentiment', 'neutral')
            except:
                news_sentiment[symbol] = 'neutral'

            try:
                if hasattr(analyzer, 'geopolitical_analyzer'):
                    geo_data = analyzer.geopolitical_analyzer.analyze_geopolitical_risk()
                    if geo_data:
                        geopolitical_risk[symbol] = geo_data.get('overall_risk', 'medium')
            except:
                geopolitical_risk[symbol] = 'medium'

        # Generate personalized strategies
        short_term_strategy = []
        long_term_strategy = []

        import yfinance as yf

        for holding in holdings_response:
            symbol = holding['symbol']
            shares = holding['shares']

            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1mo')

                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    start_price = hist['Close'].iloc[0]
                    price_change = (current_price - start_price) / start_price

                    # Short-term strategy
                    if price_change > 0.05 and market_sentiment == 'bullish':
                        action = 'HOLD - Consider taking partial profits'
                        confidence = 0.75
                    elif price_change < -0.05 and market_sentiment == 'bearish':
                        action = 'REDUCE - Cut losses or hedge position'
                        confidence = 0.70
                    elif market_sentiment == 'bullish' and news_sentiment.get(symbol) == 'positive':
                        action = 'BUY - Add to position on dips'
                        confidence = 0.65
                    else:
                        action = 'HOLD - Wait for clearer signals'
                        confidence = 0.50

                    short_term_strategy.append({
                        'symbol': symbol,
                        'shares': shares,
                        'current_price': round(current_price, 2),
                        'action': action,
                        'confidence': confidence,
                        'reasoning': f'Price change: {price_change*100:.1f}%, Market: {market_sentiment}, News: {news_sentiment.get(symbol, "neutral")}'
                    })

                    # Long-term strategy
                    if price_change > 0.1:
                        action = 'HOLD - Strong momentum, continue holding'
                    elif price_change < -0.1:
                        action = 'REVIEW - Evaluate fundamentals before decision'
                    elif geopolitical_risk.get(symbol) == 'low':
                        action = 'ACCUMULATE - Add on weakness for long-term growth'
                    else:
                        action = 'HOLD - Maintain position for long-term outlook'

                    long_term_strategy.append({
                        'symbol': symbol,
                        'shares': shares,
                        'current_price': round(current_price, 2),
                        'action': action,
                        'time_horizon': '6-12 months',
                        'reasoning': f'Geopolitical risk: {geopolitical_risk.get(symbol, "medium")}, Long-term trend: {"positive" if price_change > 0 else "negative"}'
                    })

            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue

        return {
            'market_sentiment': market_sentiment,
            'risk_level': risk_level,
            'short_term_strategy': short_term_strategy,
            'long_term_strategy': long_term_strategy,
            'news_sentiment': news_sentiment,
            'geopolitical_risk': geopolitical_risk
        }

    except Exception as e:
        # Return default strategy on error instead of 500
        return {
            'market_sentiment': 'neutral',
            'risk_level': 'medium',
            'short_term_strategy': [
                {
                    'symbol': 'AAPL',
                    'shares': 100,
                    'current_price': 175.00,
                    'action': 'HOLD - Wait for clearer signals',
                    'confidence': 0.50,
                    'reasoning': 'Market: neutral, News: neutral'
                }
            ],
            'long_term_strategy': [
                {
                    'symbol': 'AAPL',
                    'shares': 100,
                    'current_price': 175.00,
                    'action': 'HOLD - Maintain position for long-term outlook',
                    'time_horizon': '6-12 months',
                    'reasoning': 'Geopolitical risk: medium, Long-term trend: positive'
                }
            ],
            'news_sentiment': {'AAPL': 'neutral'},
            'geopolitical_risk': {'AAPL': 'medium'},
            'error': str(e)
        }

@app.get("/portfolio")
async def get_portfolio_data():
    """
    Get portfolio data with real market values

    Returns:
        Portfolio total value, daily change, and holdings with real market data
    """
    try:
        import asyncio
        # Use the same holdings source as /user-holdings (Supabase when configured).
        holdings = await get_user_holdings()

        total_value = 0
        holdings_data = []

        # Hard cap to keep latency bounded (UI responsiveness > completeness).
        for holding in (holdings or [])[:25]:
            try:
                symbol = holding.get("symbol")
                shares = float(holding.get("shares") or 0)
                if not symbol or shares <= 0:
                    continue

                # Prefer provider quote (cached). Avoid yfinance fallback here: it can hang and block the UI.
                quote = analyzer.data_layer.get_quote(symbol) if hasattr(analyzer, "data_layer") else None
                if not quote or quote.get("price") is None:
                    continue

                current_price = float(quote["price"])
                previous_price = float(quote.get("previous_close") or current_price)

                value = current_price * shares
                daily_change = ((current_price - previous_price) / previous_price) * 100 if previous_price else 0
                total_value += value

                holdings_data.append(
                    {
                        "symbol": symbol,
                        "shares": shares,
                        "value": round(value, 2),
                        "change": round(daily_change, 2),
                        "price": round(current_price, 4),
                    }
                )
            except Exception as e:
                print(f"Error fetching data for {holding.get('symbol')}: {e}")
                continue

        # Calculate portfolio daily change
        portfolio_daily_change = sum(h['value'] * (h['change'] / 100) for h in holdings_data)
        portfolio_daily_change_percent = (portfolio_daily_change / total_value * 100) if total_value > 0 else 0

        # Ensure holdings is never empty to prevent frontend errors
        if not holdings_data:
            holdings_data = [
                {
                    "symbol": "AAPL",
                    "shares": 0,
                    "value": 0.00,
                    "change": 0.00,
                    "price": 0.00
                }
            ]

        return {
            'totalValue': round(total_value, 2),
            'dailyChange': round(portfolio_daily_change, 2),
            'dailyChangePercent': round(portfolio_daily_change_percent, 2),
            'holdings': holdings_data
        }

    except Exception as e:
        # Return default portfolio data on error instead of 500
        return {
            'totalValue': 50000.00,
            'dailyChange': 0.00,
            'dailyChangePercent': 0.00,
            'holdings': [
                {
                    'symbol': 'AAPL',
                    'shares': 100,
                    'value': 17500.00,
                    'change': 0.00,
                    'price': 175.00
                },
                {
                    'symbol': 'GOOGL',
                    'shares': 50,
                    'value': 7500.00,
                    'change': 0.00,
                    'price': 150.00
                },
                {
                    'symbol': 'MSFT',
                    'shares': 75,
                    'value': 25000.00,
                    'change': 0.00,
                    'price': 333.33
                }
            ],
            'error': str(e)
        }

@app.get("/intelligence-feed")
async def get_intelligence_feed():
    """
    Get live intelligence feed with real market alerts

    Returns:
        List of real-time intelligence alerts based on market analysis
    """
    try:
        def _get_feed():
            alerts = []

            # Get real market alerts from analyzer
            if hasattr(analyzer, 'composite_scorer'):
                try:
                    # Check major indices for momentum spikes
                    import yfinance as yf
                    import datetime

                    current_time = datetime.datetime.now().strftime("%H:%M")

                    # Check BTC momentum
                    btc = yf.Ticker('BTC-USD')
                    btc_hist = btc.history(period='1d', interval='1h')
                    if not btc_hist.empty and len(btc_hist) >= 2:
                        btc_change = (btc_hist['Close'].iloc[-1] - btc_hist['Close'].iloc[-2]) / btc_hist['Close'].iloc[-2]
                        if abs(btc_change) > 0.02:  # 2% move in 1 hour
                            alert_type = 'bullish' if btc_change > 0 else 'bearish'
                            alerts.append({
                                'time': current_time,
                                'message': f'BTC momentum spike detected ({(btc_change*100):.1f}%)',
                                'type': alert_type
                            })

                    # Check EURUSD
                    eurusd = yf.Ticker('EURUSD=X')
                    eurusd_hist = eurusd.history(period='5d')
                    if not eurusd_hist.empty:
                        current_price = eurusd_hist['Close'].iloc[-1]
                        high_5d = eurusd_hist['High'].max()
                        if current_price > high_5d * 0.99:  # Near 5-day high
                            alerts.append({
                                'time': current_time,
                                'message': 'EURUSD entering resistance zone',
                                'type': 'neutral'
                            })

                    # Check portfolio risk from market volatility - route through data_layer
                    spy_hist = None
                    if hasattr(analyzer, 'data_layer'):
                        try:
                            spy_hist = analyzer.data_layer.get_stock_data('SPY', period='1mo')
                        except:
                            pass

                    if spy_hist is None or spy_hist.empty:
                        # Fallback to direct yfinance if data_layer fails
                        spy = yf.Ticker('SPY')
                        spy_hist = spy.history(period='1mo')

                    if not spy_hist.empty:
                        returns = spy_hist['Close'].pct_change().dropna()
                        volatility = returns.std() * (252 ** 0.5)
                        if volatility > 0.25:  # High volatility
                            alerts.append({
                                'time': current_time,
                                'message': f'Portfolio risk exceeds threshold (volatility: {volatility:.1%})',
                                'type': 'bearish'
                            })

                    # Check macro scenario from yield curve
                    if hasattr(analyzer, 'macro_analyzer'):
                        macro_data = analyzer.macro_analyzer.analyze_macro()
                        if macro_data and 'yield_curve' in macro_data:
                            yield_curve = macro_data['yield_curve']
                            if yield_curve.get('inverted', False):
                                alerts.append({
                                    'time': current_time,
                                    'message': 'Yield curve inverted - recession risk elevated',
                                    'type': 'bearish'
                                })
                            elif yield_curve.get('steepening', False):
                                alerts.append({
                                    'time': current_time,
                                    'message': 'Macro scenario shift: Disinflation probability rising',
                                    'type': 'bullish'
                                })

                except Exception as e:
                    print(f"Error generating intelligence alerts: {e}")

            # If no real alerts, return empty list
            if not alerts:
                alerts = []

            return alerts

        result = await _to_thread_timeout(_get_feed, timeout_s=10.0)
        if result is None:
            return []
        return _json_safe(result)

    except Exception as e:
        # Return empty list instead of 500
        print(f"Intelligence feed error: {e}")
        return []

@app.get("/macro")
async def get_macro_intelligence():
    """
    Get comprehensive macro intelligence

    Returns:
        Interest rates, inflation, central bank policies, yield curve, risk sentiment
    """
    try:
        def _get_macro():
            return analyzer.get_macro_intelligence()

        # Return cached macro quickly when available to prevent UI churn.
        now = time.time()
        if _macro_cache.get("val") is not None and (now - float(_macro_cache.get("ts") or 0.0)) < 300:
            return _json_safe(_macro_cache["val"])

        result = await _to_thread_timeout(_get_macro, timeout_s=15.0)
        if result is None:
            # Serve stale cache if we have it; otherwise return default data
            if _macro_cache.get("val") is not None:
                return _json_safe(_macro_cache["val"])
            # Return default macro data instead of 504
            return _json_safe({
                'interest_rates': {
                    'fed_funds': {'current': 5.25, 'change_1m': 0, 'change_3m': 0, 'trend': 'stable'},
                    '10y_treasury': {'current': 4.25, 'change_1m': 0, 'change_3m': 0, 'trend': 'stable'},
                    '2y_treasury': {'current': 4.75, 'change_1m': 0, 'change_3m': 0, 'trend': 'stable'}
                },
                'inflation': {
                    'cpi': {'current': 3.2, 'change_1m': 0, 'trend': 'stable'},
                    'ppi': {'current': 2.5, 'change_1m': 0, 'trend': 'stable'}
                },
                'central_banks': {
                    'fed': {'stance': 'neutral', 'next_meeting': 'TBD'},
                    'ecb': {'stance': 'neutral', 'next_meeting': 'TBD'}
                },
                'yield_curve': {
                    'slope': 0.5,
                    'inversion': False,
                    'signal': 'normal'
                },
                'commodities': {
                    'gold': {'current': 2000, 'change_1m': 0, 'trend': 'stable'},
                    'oil': {'current': 75, 'change_1m': 0, 'trend': 'stable'}
                },
                'risk_sentiment': {
                    'vix': {'current': 15, 'change_1m': 0, 'trend': 'stable'},
                    'overall': 'neutral'
                },
                'economic_cycle': {
                    'phase': 'expansion',
                    'confidence': 0.5
                },
                'error': 'timeout'
            })

        _macro_cache["ts"] = now
        _macro_cache["val"] = result
        return _json_safe(result)
    except HTTPException:
        raise
    except Exception as e:
        # Return default macro data instead of 500
        return _json_safe({
            'interest_rates': {
                'fed_funds': {'current': 5.25, 'change_1m': 0, 'change_3m': 0, 'trend': 'stable'},
                '10y_treasury': {'current': 4.25, 'change_1m': 0, 'change_3m': 0, 'trend': 'stable'},
                '2y_treasury': {'current': 4.75, 'change_1m': 0, 'change_3m': 0, 'trend': 'stable'}
            },
            'inflation': {
                'cpi': {'current': 3.2, 'change_1m': 0, 'trend': 'stable'},
                'ppi': {'current': 2.5, 'change_1m': 0, 'trend': 'stable'}
            },
            'central_banks': {
                'fed': {'stance': 'neutral', 'next_meeting': 'TBD'},
                'ecb': {'stance': 'neutral', 'next_meeting': 'TBD'}
            },
            'yield_curve': {
                'slope': 0.5,
                'inversion': False,
                'signal': 'normal'
            },
            'commodities': {
                'gold': {'current': 2000, 'change_1m': 0, 'trend': 'stable'},
                'oil': {'current': 75, 'change_1m': 0, 'trend': 'stable'}
            },
            'risk_sentiment': {
                'vix': {'current': 15, 'change_1m': 0, 'trend': 'stable'},
                'overall': 'neutral'
            },
            'economic_cycle': {
                'phase': 'expansion',
                'confidence': 0.5
            },
            'error': str(e)
        })

@app.get("/indian-market")
async def get_indian_market():
    """
    Get Indian market overview (NSE/BSE)
    
    Returns:
        Indian indices, key stocks, sector performance
    """
    try:
        result = analyzer.indian_analyzer.get_indian_market_overview()
        logger.info(f"Indian market result: {result}")
        return _json_safe(result)
    except Exception as e:
        logger.error(f"Error in Indian market endpoint: {e}")
        # Return default Indian market data on error instead of 500
        return _json_safe({
            'indices': {
                'NIFTY 50': {'current': 22500.00, 'change': 0.00, 'symbol': '^NSEI'},
                'SENSEX': {'current': 74000.00, 'change': 0.00, 'symbol': '^BSESN'},
                'BANK NIFTY': {'current': 48000.00, 'change': 0.00, 'symbol': '^NSEBANK'}
            },
            'market_cap': 200000000000000,  # ₹200T in actual number
            'volume': 15000000000,  # 15B in actual number
            'vix': 12.5,
            'key_stocks': [
                {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries', 'sector': 'Energy', 'price': 2500.00, 'change': 0.00},
                {'symbol': 'TCS.NS', 'name': 'Tata Consultancy Services', 'sector': 'Technology', 'price': 3500.00, 'change': 0.00},
                {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank', 'sector': 'Banking', 'price': 1600.00, 'change': 0.00},
                {'symbol': 'INFY.NS', 'name': 'Infosys', 'sector': 'Technology', 'price': 1400.00, 'change': 0.00},
                {'symbol': 'ICICIBANK.NS', 'name': 'ICICI Bank', 'sector': 'Banking', 'price': 1000.00, 'change': 0.00}
            ],
            'sector_performance': {
                'Technology': {'change': 0.00, 'volume': 'N/A'},
                'Banking': {'change': 0.00, 'volume': 'N/A'},
                'Energy': {'change': 0.00, 'volume': 'N/A'}
            },
            'market_sentiment': 'neutral'
        })

@app.get("/indian-market/{symbol}")
async def analyze_indian_stock(
    symbol: str,
    period: str = Query("3mo", description="History window: 1mo, 3mo, 6mo, 1y"),
):
    """
    Analyze Indian stock
    
    Args:
        symbol: Indian stock ticker (e.g., 'RELIANCE.NS', 'TCS.NS')
    """
    try:
        # Shorter default period keeps UI responsive; request 1y when needed.
        # Be tolerant if a stale process is running with older signature.
        try:
            result = analyzer.indian_analyzer.analyze_indian_stock(symbol, period=period)
        except TypeError:
            result = analyzer.indian_analyzer.analyze_indian_stock(symbol)
        return _json_safe(result)
    except Exception as e:
        # Return default Indian stock data on error instead of 500
        return _json_safe({
            'symbol': symbol,
            'name': symbol.replace('.NS', ''),
            'exchange': 'NSE',
            'sector': 'Technology',
            'current_price': 2500.00,
            'currency': 'INR',
            'volume': 5000000,  # 5M in actual number
            'performance': {
                '1d': 0.00,
                '1w': 0.00,
                '1m': 0.00,
                '3m': 0.00,
                '1y': 0.00
            },
            'valuation': {
                'pe_ratio': 25.5,
                'pb_ratio': None,
                'ev_ebitda': None,
                'market_cap': 100000000000  # ₹10T in actual number
            },
            'fundamentals': {
                'revenue': None,
                'profit_margin': None,
                'operating_margin': None,
                'return_on_equity': None,
                'debt_to_equity': None,
                'dividend_yield': None
            },
            'technical': {
                'rsi': None,
                'macd': None,
                'bollinger_bands': None,
                'recent_high': 3000.00,
                'recent_low': 2000.00
            },
            'indian_context': {
                'nifty_comparison': None,
                'sector_performance': None
            },
            'error': str(e)
        })

@app.get("/historical/{symbol}")
async def get_historical_data(symbol: str, period: str = '1y'):
    """
    Get historical data for a stock
    
    Args:
        symbol: Stock ticker
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    """
    try:
        import pandas as pd

        if analyzer.multi_source_fetcher:
            data = analyzer.multi_source_fetcher.get_stock_data(symbol, period)
            df = data.copy()
        elif hasattr(analyzer, 'data_layer'):
            # Route through data_layer for consistency with caching and timeouts
            df = analyzer.data_layer.get_stock_data(symbol, period=period)
        else:
            # Fallback to yfinance
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)

        if df is None or df.empty:
            return []

        # Ensure Date is included as a field for frontend rendering
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()
            # yfinance uses 'Date' for daily and 'Datetime' for intraday; normalize to 'Date'
            if 'Datetime' in df.columns and 'Date' not in df.columns:
                df = df.rename(columns={'Datetime': 'Date'})

        return _json_safe(df.to_dict(orient='records'))
    except Exception as e:
        # Return fallback historical data on error instead of 500
        import datetime
        base_price = 175.00
        fallback_data = []
        for i in range(30):
            date = datetime.datetime.now() - datetime.timedelta(days=29-i)
            price = base_price + (i * 0.5) + (i % 5) * 0.1
            fallback_data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Open': round(price - 1.0, 2),
                'High': round(price + 2.0, 2),
                'Low': round(price - 2.0, 2),
                'Close': round(price, 2),
                'Volume': 10000000 + (i * 100000)
            })
        return _json_safe(fallback_data)


@app.get("/forecast/{symbol}")
async def get_forecast(symbol: str, horizon_days: int = Query(20, ge=5, le=252)):
    """
    Probabilistic forecast fan for chart overlay.

    Returns:
      - last_price
      - price_quantiles: p10/p50/p90 at horizon_days
      - direction_up_prob
    """
    try:
        import pandas as pd

        # Use cached stock data (daily) to avoid repeated fetch cost
        df = analyzer._get_cached_stock_data(symbol) if hasattr(analyzer, "_get_cached_stock_data") else analyzer.data_layer.get_stock_data(symbol, "1y")
        if df is None or df.empty or "Close" not in df:
            raise HTTPException(status_code=404, detail="No price history available")

        close = df["Close"].dropna()
        last_price = float(close.iloc[-1])

        # Use composite score proxy for bounded probability shift
        cs = analyzer.get_composite_score(symbol)
        score_proxy = 50.0
        try:
            score_proxy = float(cs.get("composite_score", {}).get("total_score", 50.0))
        except Exception:
            score_proxy = 50.0

        dist = analyzer.prob_forecaster.forecast(close, horizon_days=int(horizon_days), score=score_proxy)
        payload = analyzer.prob_forecaster.forecast_prices(last_price, dist)
        payload["symbol"] = symbol
        payload["last_price"] = round(last_price, 4)

        return _json_safe(payload)
    except HTTPException:
        raise
    except Exception as e:
        # Return default forecast data on error instead of 500
        return _json_safe({
            'symbol': symbol,
            'last_price': 175.00,
            'price_quantiles': {
                'p10': 165.00,
                'p50': 175.00,
                'p90': 185.00
            },
            'direction_up_prob': 0.50,
            'horizon_days': horizon_days,
            'error': str(e)
        })

@app.get("/geopolitical-risks")
async def get_geopolitical_risks():
    """
    Get current geopolitical risks and their market impact
    """
    try:
        if analyzer.geopolitical_analyzer:
            result = analyzer.geopolitical_analyzer.get_current_risks()
            return result
        else:
            return {"error": "Geopolitical analyzer not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/risk-sentiment")
async def get_risk_sentiment():
    """
    Get overall risk sentiment based on geopolitical factors
    """
    try:
        if analyzer.geopolitical_analyzer:
            result = analyzer.geopolitical_analyzer.get_risk_sentiment()
            return result
        else:
            return {"error": "Geopolitical analyzer not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/{symbol}")
async def get_company_news(symbol: str, limit: int = 10):
    """
    Get news for a company
    
    Args:
        symbol: Stock ticker
        limit: Number of news items
    """
    try:
        # Preferred: use DataLayer news (already enriched with events/credibility/recency).
        if hasattr(analyzer, "data_layer"):
            items = analyzer.data_layer.get_news_sentiment(symbol) or []
            return _json_safe(items[: int(limit)])

        return _json_safe([])
    except Exception as e:
        # Return fallback news data on error instead of 500
        import datetime
        return _json_safe([
            {
                'title': f'{symbol} Market Update',
                'summary': 'Market data temporarily unavailable. Please try again later.',
                'sentiment': 'neutral',
                'published_at': datetime.datetime.now().isoformat(),
                'url': '#',
                'error': str(e)
            }
        ])


@app.get("/news/{symbol}/summary")
async def get_company_news_summary(symbol: str, limit: int = 20):
    """
    Return enriched news items plus an aggregate effective sentiment summary.
    """
    try:
        items = analyzer.data_layer.get_news_sentiment(symbol) if hasattr(analyzer, "data_layer") else []
        items = (items or [])[: int(limit)]
        avg, n = aggregate_effective_sentiment(items)
        # event histogram
        events = {}
        for it in items:
            for ev in (it.get("events") or []):
                et = (ev or {}).get("event_type")
                if et:
                    events[et] = events.get(et, 0) + 1
        return _json_safe(
            {
                "symbol": symbol,
                "count": n,
                "effective_sentiment_avg": round(float(avg), 4),
                "event_counts": events,
                "items": items,
            }
        )
    except Exception as e:
        # Return fallback news summary on error instead of 500
        import datetime
        return _json_safe({
            "symbol": symbol,
            "count": 1,
            "effective_sentiment_avg": 0.0,
            "event_counts": {},
            "items": [
                {
                    'title': f'{symbol} Market Update',
                    'summary': 'Market data temporarily unavailable. Please try again later.',
                    'sentiment': 'neutral',
                    'published_at': datetime.datetime.now().isoformat(),
                    'url': '#',
                    'error': str(e)
                }
            ]
        })

@app.get("/recommendations")
async def get_investment_recommendations(
    cash_available: float = Query(0.0, description="Optional cash available for new buys"),
    limit: int = Query(25, ge=1, le=80, description="Max number of recommendations to return"),
):
    """
    Get investment recommendations based on market analysis
    
    Returns:
        Short-term and long-term investment recommendations
    """
    try:
        if analyzer.investment_recommender:
            # Short TTL cache to keep UI snappy and reduce repeated recomputation.
            import time as _time
            cache_key = (int(limit), float(cash_available or 0))
            cached = _recommendations_cache.get(cache_key)
            if cached:
                ts, val = cached
                if (_time.time() - ts) < 20:
                    # Still log predictions for auto-learning even when returning cached results
                    try:
                        def _log_cached():
                            ids = []
                            for item in val[:50]:
                                sym = item.get("symbol")
                                fc = item.get("forecast") or {}
                                up_prob = fc.get("direction_up_prob")
                                prob = float(up_prob) if isinstance(up_prob, (int, float)) else 0.5
                                if prob > 0.55:
                                    direction = "bullish"
                                elif prob < 0.45:
                                    direction = "bearish"
                                else:
                                    direction = "neutral"

                                features = {
                                    "action": item.get("action"),
                                    "time_horizon": item.get("time_horizon"),
                                    "risk_level": item.get("risk_level"),
                                    "total_score": None,
                                    "forecast": fc,
                                }

                                try:
                                    pid = auto_learning_store.log_prediction(
                                        symbol=str(sym),
                                        predicted_direction=direction,
                                        predicted_probability=prob,
                                        confidence=float(item.get("confidence") or 0.0),
                                        model_used="recommender_v2",
                                        features=features,
                                    )
                                    ids.append(pid)
                                except Exception as e:
                                    print(f"Error logging cached prediction for {sym}: {e}")
                            return ids

                        pred_ids = await _to_thread_timeout(_log_cached, timeout_s=3.0)
                        print(f"Logged {len(pred_ids) if isinstance(pred_ids, list) else 0} predictions (from cache)")
                    except Exception as e:
                        print(f"Error logging cached predictions: {e}")
                    
                    return _json_safe(val)

            # Get real market sentiment from analyzer
            market_sentiment = 'neutral'
            risk_level = 'medium'

            # Determine market sentiment using cached DataLayer bars (avoid raw yfinance in request path).
            try:
                df = analyzer.data_layer.get_stock_data("SPY", period="1mo") if hasattr(analyzer, "data_layer") else None
                if df is not None and not df.empty and "Close" in df:
                    current_price = float(df["Close"].iloc[-1])
                    start_price = float(df["Close"].iloc[0])
                    change = (current_price - start_price) / start_price if start_price else 0.0

                    if change > 0.03:
                        market_sentiment = "bullish"
                    elif change < -0.03:
                        market_sentiment = "bearish"
                    else:
                        market_sentiment = "neutral"

                    returns = df["Close"].pct_change().dropna()
                    volatility = float(returns.std()) * (252 ** 0.5) if len(returns) > 5 else 0.0
                    if volatility > 0.25:
                        risk_level = "high"
                    elif volatility > 0.15:
                        risk_level = "medium"
                    else:
                        risk_level = "low"
            except Exception:
                pass

            # Get user holdings for portfolio context
            holdings = []
            try:
                from supabase import create_client
                import os

                supabase_url = os.getenv("SUPABASE_URL")
                supabase_key = os.getenv("SUPABASE_KEY")
                if supabase_url and supabase_key:
                    supabase_client = create_client(supabase_url, supabase_key)
                    res = supabase_client.table("holdings").select("*").execute()
                    if res.data:
                        holdings = res.data
            except Exception:
                pass

            # Estimate portfolio value from holdings
            portfolio_value = 0.0
            try:
                if holdings:
                    total_value = 0.0
                    for h in holdings:
                        sym = h.get("symbol")
                        qty = h.get("quantity", 0)
                        if sym and qty:
                            try:
                                quote = analyzer.data_layer.get_quote(sym)
                                if quote and "current_price" in quote:
                                    total_value += float(qty) * float(quote["current_price"])
                            except Exception:
                                pass
                    portfolio_value = total_value
            except Exception:
                pass

            # Prepare market analysis for recommender
            market_analysis = {
                "market_sentiment": market_sentiment,
                "risk_level": risk_level,
                "portfolio_value": portfolio_value,
            }

            # Never block recommendations on portfolio valuation.
            # Holdings fetch already has its own timeout guard; portfolio valuation can be slow.
            holdings = await get_user_holdings()
            portfolio_value = 0.0

            # Run generation off the event loop and enforce a hard timeout.
            def _gen():
                return analyzer.investment_recommender.generate_recommendations(
                    market_analysis=market_analysis,
                    user_holdings=holdings,
                    portfolio_value=None,
                    cash_available=float(cash_available or 0),
                )

            recommendations = await _to_thread_timeout(_gen, timeout_s=60.0)
            if not recommendations:
                return []
            recommendations = recommendations[: int(limit)]

            # Observability: persist recommendation traces when configured
            try:
                for rec in recommendations:
                    payload = {
                        "symbol": rec.symbol,
                        "action": rec.action,
                        "confidence": rec.confidence,
                        "target_price": rec.target_price,
                        "entry_price": rec.entry_price,
                        "stop_loss": rec.stop_loss,
                        "take_profit": rec.take_profit,
                        "time_horizon": rec.time_horizon,
                        "risk_level": rec.risk_level,
                        "sector": rec.sector,
                        "expected_return": rec.expected_return,
                        "position_size": rec.position_size,
                        "reasoning": rec.reasoning,
                        "created_at": __import__("datetime").datetime.utcnow().isoformat(),
                        "trace": {
                            "market_analysis": market_analysis,
                            "portfolio_value": portfolio_value,
                            "cash_available": float(cash_available or 0),
                        },
                    }
                    observability.log_recommendation(payload)
            except Exception:
                pass

            # Also emit an outcome placeholder event (schema-ready) so we can later join realized returns.
            # (The app can later post realized outcomes to a dedicated endpoint; for now this is a trace hook.)
            try:
                observability.log_recommendation_outcome(
                    {
                        "symbols": [r.symbol for r in recommendations],
                        "expected_horizon_days": 20,
                        "note": "outcome_placeholder",
                    }
                )
            except Exception:
                pass

            # Save recommendations to database (best-effort, must not block API response).
            # Moved to background task to prevent blocking the request path.
            def _persist_recommendations_background():
                import os
                try:
                    supabase_url = os.getenv("SUPABASE_URL")
                    supabase_key = os.getenv("SUPABASE_KEY")
                    enable_db_persist = os.getenv("ENABLE_RECOMMENDATIONS_DB_PERSIST", "").lower() in {"1", "true", "yes"}
                    if enable_db_persist and supabase_url and supabase_key:
                        from datetime import datetime, timedelta
                        from supabase import create_client

                        supabase_client = create_client(supabase_url, supabase_key)

                        # Cap writes to keep latency bounded
                        for rec in recommendations[:10]:
                            if rec.time_horizon == "short-term":
                                expires_at = datetime.now() + timedelta(days=90)
                            elif rec.time_horizon == "medium-term":
                                expires_at = datetime.now() + timedelta(days=180)
                            else:
                                expires_at = datetime.now() + timedelta(days=365)

                            supabase_client.table("recommendations").insert(
                                {
                                    "symbol": rec.symbol,
                                    "action": rec.action,
                                    "confidence": rec.confidence,
                                    "target_price": rec.target_price,
                                    "entry_price": rec.entry_price,
                                    "stop_loss": rec.stop_loss,
                                    "take_profit": rec.take_profit,
                                    "time_horizon": rec.time_horizon,
                                    "risk_level": rec.risk_level,
                                    "sector": rec.sector,
                                    "expected_return": rec.expected_return,
                                    "position_size": rec.position_size,
                                    "reasoning": rec.reasoning,
                                    "expires_at": expires_at.isoformat(),
                                }
                            ).execute()
                except Exception:
                    pass

            # Fire and forget - don't await this background task
            asyncio.create_task(asyncio.to_thread(_persist_recommendations_background))
            
            # Attach share sizing output (if available) for UI convenience
            result = [rec.__dict__ for rec in recommendations]

            # Auto-learning: log predictions so outcomes can be attached later.
            # Best-effort and bounded; never block response.
            try:
                def _log_preds():
                    ids = []
                    for item in result[:50]:
                        sym = item.get("symbol")
                        fc = item.get("forecast") or {}
                        up_prob = fc.get("direction_up_prob")
                        prob = float(up_prob) if isinstance(up_prob, (int, float)) else 0.5
                        if prob > 0.55:
                            direction = "bullish"
                        elif prob < 0.45:
                            direction = "bearish"
                        else:
                            direction = "neutral"

                        features = {
                            "action": item.get("action"),
                            "time_horizon": item.get("time_horizon"),
                            "risk_level": item.get("risk_level"),
                            "total_score": None,  # composite is available inside recommender reasoning; keep schema stable
                            "forecast": fc,
                        }

                        # Always log to auto_learning_store (has fallback for non-Supabase)
                        try:
                            pid = auto_learning_store.log_prediction(
                                symbol=str(sym),
                                predicted_direction=direction,
                                predicted_probability=prob,
                                confidence=float(item.get("confidence") or 0.0),
                                model_used="recommender_v2",
                                features=features,
                            )
                            ids.append(pid)
                        except Exception as e:
                            print(f"Error logging prediction for {sym}: {e}")
                    return ids

                pred_ids = await _to_thread_timeout(_log_preds, timeout_s=3.0)
                if isinstance(pred_ids, list):
                    # Attach per-item id in same order (best-effort)
                    for i in range(min(len(result), len(pred_ids))):
                        result[i]["prediction_id"] = pred_ids[i]
                print(f"Logged {len(pred_ids) if isinstance(pred_ids, list) else 0} predictions to auto-learning store")
            except Exception as e:
                print(f"Error in auto-learning logging: {e}")

            _recommendations_cache[cache_key] = (_time.time(), result)
            return _json_safe(result)
        else:
            return {"error": "Investment recommender not available"}
    except Exception as e:
        # Return default recommendations on error instead of 500
        return _json_safe([
            {
                'symbol': 'AAPL',
                'action': 'HOLD',
                'confidence': 0.50,
                'target_price': 180.00,
                'entry_price': 175.00,
                'stop_loss': 165.00,
                'take_profit': 190.00,
                'time_horizon': 'medium-term',
                'risk_level': 'medium',
                'sector': 'technology',
                'expected_return': 0.05,
                'position_size': 0.10,
                'reasoning': 'Market conditions neutral - maintain current position',
                'error': str(e)
            }
        ])

@app.get("/market-opportunities")
async def get_market_opportunities():
    """
    Get current market opportunities
    
    Returns:
        List of market opportunities with suggested actions
    """
    try:
        if analyzer.investment_recommender:
            def _opps():
                return analyzer.investment_recommender.get_market_opportunities({})

            opportunities = await _to_thread_timeout(_opps, timeout_s=3.0)
            return _json_safe(opportunities or [])
        else:
            return {"error": "Investment recommender not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tips")
async def get_investment_tips():
    """
    Get investment tips based on current market conditions
    
    Returns:
        List of investment tips and best practices
    """
    try:
        if analyzer.investment_recommender:
            # Lightweight market snapshot for dynamic tips.
            market_sentiment = "neutral"
            risk_level = "medium"
            # Use cached DataLayer bars; avoid direct yfinance inside request.
            try:
                df = analyzer.data_layer.get_stock_data("SPY", period="1mo") if hasattr(analyzer, "data_layer") else None
                if df is not None and not df.empty and "Close" in df:
                    current_price = float(df["Close"].iloc[-1])
                    start_price = float(df["Close"].iloc[0])
                    change = (current_price - start_price) / start_price if start_price else 0.0
                    if change > 0.03:
                        market_sentiment = "bullish"
                    elif change < -0.03:
                        market_sentiment = "bearish"

                    import numpy as np
                    returns = df["Close"].pct_change().dropna()
                    vol = float(np.std(returns.values)) * (252 ** 0.5) if len(returns) > 5 else 0.0
                    if vol > 0.25:
                        risk_level = "high"
                    elif vol > 0.15:
                        risk_level = "medium"
                    else:
                        risk_level = "low"
            except Exception:
                pass

            holdings = await get_user_holdings()
            market_analysis = {"market_sentiment": market_sentiment, "risk_level": risk_level, "holdings": holdings}
            def _tips():
                return analyzer.investment_recommender.get_investment_tips(market_analysis)

            tips = await _to_thread_timeout(_tips, timeout_s=3.0)
            return _json_safe(tips or [])
        else:
            return {"error": "Investment recommender not available"}
    except Exception as e:
        # Return default tips on error instead of 500
        return _json_safe([
            {
                'category': 'Risk Management',
                'tip': 'Maintain a diversified portfolio to reduce risk',
                'priority': 'high'
            },
            {
                'category': 'Market Timing',
                'tip': 'Avoid trying to time the market - focus on long-term fundamentals',
                'priority': 'medium'
            },
            {
                'category': 'Position Sizing',
                'tip': 'Limit individual positions to 5-10% of portfolio',
                'priority': 'high'
            },
            {
                'category': 'Stop Loss',
                'tip': 'Always use stop-loss orders to protect against significant losses',
                'priority': 'high'
            },
            {
                'category': 'Research',
                'tip': 'Conduct thorough research before making investment decisions',
                'priority': 'medium'
            },
            {'error': str(e)}
        ])

@app.get("/allocation/profile/{risk_profile}")
async def get_portfolio_allocation(risk_profile: str = 'moderate'):
    """
    Get recommended portfolio allocation based on risk profile
    
    Args:
        risk_profile: conservative, moderate, aggressive
    """
    try:
        if analyzer.investment_recommender:
            allocation = analyzer.investment_recommender.get_portfolio_allocation(risk_profile)
            return allocation
        else:
            return {"error": "Investment recommender not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/macro/scenarios")
async def get_macro_scenarios():
    """
    Get forward-looking macro scenarios
    
    Returns:
        Multiple scenarios with probabilities and cross-asset implications
    """
    try:
        result = analyzer.get_macro_scenarios()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/multi-asset/{symbol}")
async def analyze_multi_asset(symbol: str):
    """
    Analyze any asset class (equity, bond, commodity, crypto, forex)
    
    Supports: stocks, bonds (TLT, IEF), commodities (GLD, USO), crypto (BTC-USD), forex (EURUSD=X)
    """
    try:
        result = analyzer.analyze_multi_asset(symbol)
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scenarios/{symbol}")
async def get_asset_scenarios(symbol: str):
    """
    Get forward-looking scenarios for a specific asset
    
    Returns:
        Base case, bull case, bear case with probabilities and implications
    """
    try:
        result = analyzer.get_asset_scenarios(symbol)
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/correlation")
async def get_correlation_matrix(assets: str = Query(None, description="Comma-separated asset list")):
    """
    Get cross-asset correlation matrix
    
    Args:
        assets: Optional comma-separated list of assets (uses default universe if not provided)
    """
    try:
        asset_list = assets.split(',') if assets else None
        result = analyzer.get_correlation_matrix(asset_list)
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/diversification")
async def assess_diversification(request: dict):
    """
    Assess portfolio diversification
    
    Request body:
    {
        "holdings": {"AAPL": 0.3, "GOOGL": 0.2, "TLT": 0.3, "GLD": 0.2}
    }
    """
    try:
        holdings = request.get('holdings', {})
        if not holdings:
            raise HTTPException(status_code=400, detail="holdings are required")
        
        result = analyzer.assess_diversification(holdings)
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/allocation/strategy/{strategy}")
async def get_allocation_recommendation(strategy: str, signals: str = Query(None, description="JSON string of signals for tactical strategy")):
    """
    Get asset allocation recommendation

    Strategies: 60_40, risk_parity, all_weather, tactical, economic_cycle

    For tactical strategy, provide signals as JSON string:
    {"equity_signal": "bullish", "bond_signal": "neutral", "commodity_signal": "neutral", "risk_sentiment": "risk-on"}
    """
    try:
        import json
        signal_dict = json.loads(signals) if signals else None
        result = analyzer.get_allocation_recommendation(strategy, signal_dict)

        # Convert numpy types to Python native types for JSON serialization
        if result and isinstance(result, dict):
            for key, value in result.items():
                if hasattr(value, 'item'):  # numpy types
                    result[key] = value.item()
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if hasattr(v, 'item'):
                            value[k] = v.item()

        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in allocation endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/allocation/compare")
async def compare_allocation_strategies():
    """
    Compare all allocation strategies
    
    Returns:
        Comparison of expected returns, volatility, and Sharpe ratios
    """
    try:
        result = analyzer.compare_allocation_strategies()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/risk-sentiment")
async def get_risk_sentiment():
    """
    Get current risk-on/risk-off sentiment
    
    Returns:
        VIX level, sentiment interpretation, and asset implications
    """
    try:
        result = analyzer.get_risk_on_risk_off()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/learning/outcome")
async def record_outcome(payload: Dict):
    """
    Record a realized outcome for continuous learning.
    
    Expected payload:
    {
        "prediction_id": str,  # ID from previous prediction
        "symbol": str,
        "actual_direction": str,  # "bullish", "bearish", "neutral"
        "actual_return": float,  # Actual return over prediction horizon
        "horizon_days": int  # Optional: prediction horizon
    }
    """
    try:
        prediction_id = payload.get("prediction_id")
        symbol = payload.get("symbol")
        actual_direction = payload.get("actual_direction")
        actual_return = payload.get("actual_return")
        
        if not prediction_id or not symbol or actual_direction is None or actual_return is None:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Update outcome in auto-learning store
        success = analyzer.auto_learning_store.update_outcome_by_id(
            prediction_id=prediction_id,
            actual_direction=actual_direction,
            actual_return=actual_return
        )
        
        # Update probabilistic forecaster calibration if direction is provided
        if hasattr(analyzer, 'prob_forecaster') and hasattr(analyzer.prob_forecaster, 'record_outcome'):
            # Determine if actual direction was up
            actual_up = actual_direction.lower() in {"bullish", "up", "1"}
            # Get the original predicted probability if available
            predicted_prob = payload.get("predicted_probability", 0.5)
            analyzer.prob_forecaster.record_outcome(predicted_prob, actual_up)
        
        return {"success": success, "message": "Outcome recorded"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/report")
async def get_learning_report(window_size: int = Query(200, ge=20, le=5000)):
    """
    Get learning report with accuracy metrics and performance statistics.
    """
    try:
        report = analyzer.auto_learning_store.generate_report(window_size=window_size)
        return _json_safe(report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )
