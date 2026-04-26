# Netlify Function for health check
import json
from shared import get_analyzer, json_response, handle_cors

def handler(event, context):
    """Health check endpoint"""
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return handle_cors()
    
    try:
        analyzer = get_analyzer()
        return json_response({
            "status": "ok",
            "version": "3.0.0",
            "service": "netlify-function"
        })
    except Exception as e:
        return json_response({
            "status": "error",
            "error": str(e)
        }, status_code=500)
