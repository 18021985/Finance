import json
import os
import sys
from shared import get_analyzer, json_response, handle_cors

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return handle_cors()
    
    try:
        analyzer = get_analyzer()
        result = analyzer.get_macro_intelligence()
        return json_response(result)
    except Exception as e:
        return json_response({"error": str(e)}, status_code=500)
