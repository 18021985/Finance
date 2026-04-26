# Main Netlify Function for API routing
# This function handles all API routes
import json
import os
import sys
from shared import get_analyzer, json_response, handle_cors

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def handler(event, context):
    """Main API handler - routes requests to appropriate analyzer methods"""
    
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return handle_cors()
    
    try:
        analyzer = get_analyzer()
        path = event.get('path', '').replace('/.netlify/functions/api', '')
        method = event.get('httpMethod', 'GET')
        
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        path_params = event.get('pathParameters') or {}
        
        # Parse body for POST requests
        body = None
        if method == 'POST':
            try:
                body = json.loads(event.get('body', '{}'))
            except:
                body = {}
        
        # Route handling
        if path == '/health' or path == '':
            return handle_health(analyzer)
        
        elif path == '/macro-intelligence':
            return handle_macro_intelligence(analyzer)
        
        elif path == '/intelligence-feed':
            return handle_intelligence_feed(analyzer)
        
        elif path == '/composite-score':
            symbol = query_params.get('symbol', 'AAPL')
            return handle_composite_score(analyzer, symbol)
        
        elif path == '/strategies':
            return handle_strategies(analyzer)
        
        elif path == '/indian-market':
            return handle_indian_market(analyzer)
        
        elif path.startswith('/indian-market/'):
            symbol = path.split('/')[-1]
            return handle_indian_stock(analyzer, symbol)
        
        elif path == '/macro/scenarios':
            return handle_macro_scenarios(analyzer)
        
        elif path.startswith('/scenarios/'):
            symbol = path.split('/')[-1]
            return handle_asset_scenarios(analyzer, symbol)
        
        elif path.startswith('/multi-asset/'):
            symbol = path.split('/')[-1]
            return handle_multi_asset(analyzer, symbol)
        
        elif path == '/recommendations':
            return handle_recommendations(analyzer)
        
        elif path == '/auto-learning/status':
            return handle_auto_learning_status(analyzer)
        
        else:
            return json_response({
                "error": "Endpoint not found",
                "path": path
            }, status_code=404)
            
    except Exception as e:
        import traceback
        return json_response({
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status_code=500)

def handle_health(analyzer):
    """Health check"""
    return json_response({
        "status": "ok",
        "version": "3.0.0",
        "service": "netlify-function"
    })

def handle_macro_intelligence(analyzer):
    """Get macro intelligence"""
    try:
        result = analyzer.get_macro_intelligence()
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)

def handle_intelligence_feed(analyzer):
    """Get intelligence feed"""
    try:
        result = analyzer.get_intelligence_feed()
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)

def handle_composite_score(analyzer, symbol):
    """Get composite score for a symbol"""
    try:
        result = analyzer.get_composite_score(symbol)
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)

def handle_strategies(analyzer):
    """Get strategies"""
    try:
        result = analyzer.get_strategies()
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)

def handle_indian_market(analyzer):
    """Get Indian market overview"""
    try:
        result = analyzer.indian_analyzer.get_indian_market_overview()
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)

def handle_indian_stock(analyzer, symbol):
    """Analyze Indian stock"""
    try:
        result = analyzer.indian_analyzer.analyze_indian_stock(symbol)
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)

def handle_macro_scenarios(analyzer):
    """Get macro scenarios"""
    try:
        result = analyzer.get_macro_scenarios()
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)

def handle_asset_scenarios(analyzer, symbol):
    """Get asset scenarios"""
    try:
        result = analyzer.get_asset_scenarios(symbol)
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)

def handle_multi_asset(analyzer, symbol):
    """Analyze multi-asset"""
    try:
        result = analyzer.multi_asset_analyzer.analyze_asset(symbol)
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)

def handle_recommendations(analyzer):
    """Get recommendations"""
    try:
        result = analyzer.get_recommendations()
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)

def handle_auto_learning_status(analyzer):
    """Get auto-learning status"""
    try:
        result = analyzer.auto_learning.get_status()
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)
