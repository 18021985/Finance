# Shared utilities for Netlify Functions
# This module contains the analyzer classes that can be imported by individual functions

import sys
import os

# Add parent directory to path to import analyzers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from analyzer import FinancialIntelligenceSystem

# Initialize analyzers (singleton pattern)
_analyzer = None

def get_analyzer():
    """Get or create the analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = FinancialIntelligenceSystem()
    return _analyzer

def json_response(data, status_code=200):
    """Helper to create JSON response for Netlify Functions"""
    import json
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps(data)
    }

def handle_cors():
    """Handle CORS preflight requests"""
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': ''
    }
