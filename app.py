#!/usr/bin/env python3
"""
Facebook Token Tool - Backend Server
Deploy on Render.com
"""

import json
import urllib.parse
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Token Types Configuration
TOKEN_OPTIONS = [
    {"value": "EAAAAU", "name": "EAAAAU - Standard Token", "description": "General purpose access token"},
    {"value": "EAAD", "name": "EAAD - Basic Token", "description": "Basic authentication token"},
    {"value": "EAAAAAY", "name": "EAAAAAY - Extended Token", "description": "Extended lifetime token"},
    {"value": "EAADYP", "name": "EAADYP - Page Token", "description": "Facebook Page access token"},
    {"value": "EAAD6V7", "name": "EAAD6V7 - App Token", "description": "Application access token"},
    {"value": "EAAC2SPKT", "name": "EAAC2SPKT - Graph API Token", "description": "Graph API access token"},
    {"value": "EAAGOfO", "name": "EAAGOfO - Business Token", "description": "Business Manager token"},
    {"value": "EAAVB", "name": "EAAVB - Video Token", "description": "Video streaming access"},
    {"value": "EAAC4", "name": "EAAC4 - Ads Token", "description": "Facebook Ads API token"},
    {"value": "EAACW5F", "name": "EAACW5F - Marketing Token", "description": "Marketing API access"},
    {"value": "EAAB", "name": "EAAB - Basic Auth Token", "description": "Basic authorization token"},
    {"value": "EAAQ", "name": "EAAQ - Query Token", "description": "FQL query access"},
    {"value": "EAAGNO4", "name": "EAAGNO4 - Notification Token", "description": "Notifications access"},
    {"value": "EAAH", "name": "EAAH - High Security Token", "description": "High security mode"},
    {"value": "EAAC", "name": "EAAC - Commerce Token", "description": "Commerce API access"},
    {"value": "EAAClA", "name": "EAAClA - Live Token", "description": "Live streaming access"},
    {"value": "EAATK", "name": "EAATK - Tracking Token", "description": "Analytics tracking"},
    {"value": "EAAI7", "name": "EAAI7 - Instagram Token", "description": "Instagram API access"},
]

API_BASE_URL = "https://adidaphat.site/facebook/tokentocookie"

def find_token_in_data(data):
    """
    Recursively search for 'token' in nested JSON data
    """
    if isinstance(data, dict):
        # Check for token key in dictionary
        if 'token' in data:
            return data['token']
        # Search in all values
        for value in data.values():
            result = find_token_in_data(value)
            if result:
                return result
    elif isinstance(data, list):
        # Search in all list items
        for item in data:
            result = find_token_in_data(item)
            if result:
                return result
    return None

@app.route('/')
def home():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'online',
        'service': 'Facebook Token Tool',
        'version': '1.0.0',
        'options_available': len(TOKEN_OPTIONS)
    })

@app.route('/api/options', methods=['GET'])
def get_token_options():
    """Return available token types"""
    return jsonify({
        'success': True,
        'options': TOKEN_OPTIONS,
        'count': len(TOKEN_OPTIONS)
    })

@app.route('/api/extract', methods=['POST'])
def extract_token():
    """
    Extract token from Facebook cookie
    Expected JSON: {'token_type': 'EAAAAU', 'cookie': 'c_user=...;xs=...'}
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        token_type = data.get('token_type')
        cookie = data.get('cookie')
        
        # Validate inputs
        if not token_type or not cookie:
            return jsonify({
                'success': False,
                'error': 'Both token_type and cookie are required'
            }), 400
        
        # Validate token type
        valid_types = [opt['value'] for opt in TOKEN_OPTIONS]
        if token_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid token type. Must be one of: {", ".join(valid_types[:5])}...'
            }), 400
        
        # Prepare API request
        params = {
            'type': token_type,
            'cookie': cookie.strip()
        }
        
        # Build URL with parameters
        query_string = urllib.parse.urlencode(params)
        api_url = f"{API_BASE_URL}?{query_string}"
        
        # Call external API with timeout
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'error': 'Request timeout. The external API is taking too long to respond.'
            }), 504
        except requests.exceptions.RequestException as e:
            return jsonify({
                'success': False,
                'error': f'External API error: {str(e)}'
            }), 502
        
        # Parse response
        try:
            api_response = response.json()
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': 'Invalid response from external API',
                'raw_response': response.text[:500] + ('...' if len(response.text) > 500 else '')
            }), 500
        
        # Extract token from response
        token = find_token_in_data(api_response)
        
        if token:
            return jsonify({
                'success': True,
                'token': token,
                'token_type': token_type,
                'message': 'Token extracted successfully',
                'length': len(token)
            })
        else:
            # Try to find any string that looks like a token
            import re
            response_text = json.dumps(api_response)
            token_patterns = [
                r'EAA[UADQCIHKYNW]\w+',
                r'EAAB\w+',
                r'EAAC\w+',
                r'EAAD\w+',
                r'EAAE\w+',
                r'EAAF\w+',
                r'EAAG\w+',
                r'EAAH\w+',
                r'EAAI\w+',
                r'EAAJ\w+',
                r'EAAK\w+',
                r'EAAL\w+',
                r'EAAM\w+',
                r'EAAN\w+',
                r'EAAO\w+',
                r'EAAP\w+',
                r'EAAQ\w+',
                r'EAAR\w+',
                r'EAAS\w+',
                r'EAAT\w+',
                r'EAAU\w+',
                r'EAAV\w+',
                r'EAAW\w+',
                r'EAAX\w+',
                r'EAAY\w+',
                r'EAAZ\w+',
            ]
            
            for pattern in token_patterns:
                matches = re.findall(pattern, response_text)
                if matches:
                    token = matches[0]
                    return jsonify({
                        'success': True,
                        'token': token,
                        'token_type': token_type,
                        'message': 'Token found using pattern matching',
                        'length': len(token)
                    })
            
            return jsonify({
                'success': False,
                'error': 'No token found in API response',
                'api_response': api_response
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Get port from environment variable (for Render.com)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False in production
    )
