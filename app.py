from flask import Flask, request, jsonify
import requests
import json
import urllib.parse
import os

app = Flask(__name__)

# Token options from your original script
TOKEN_OPTIONS = [
    "EAAAAU", "EAAD", "EAAAAAY", "EAADYP", "EAAD6V7", "EAAC2SPKT",
    "EAAGOfO", "EAAVB", "EAAC4", "EAACW5F", "EAAB", "EAAQ",
    "EAAGNO4", "EAAH", "EAAC", "EAAClA", "EAATK", "EAAI7",
]

API_URL = "https://adidaphat.site/facebook/tokentocookie"

def find_token(data):
    """Find token in JSON response"""
    if isinstance(data, dict):
        if 'token' in data:
            return data['token']
        for v in data.values():
            result = find_token(v)
            if result:
                return result
    elif isinstance(data, list):
        for i in data:
            result = find_token(i)
            if result:
                return result
    return None

# SIMPLE HTML PAGE - NO TEMPLATES NEEDED
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Facebook Token Extractor</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #1a237e 0%, #311b92 100%);
                color: white;
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            h1 { 
                color: #bb86fc; 
                text-align: center; 
                margin-bottom: 20px;
                font-size: 2.5rem;
            }
            .btn {
                background: #bb86fc;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                margin: 10px 0;
                width: 100%;
            }
            .btn:hover { background: #9c64f7; }
            textarea {
                width: 100%;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid rgba(255,255,255,0.3);
                background: rgba(0,0,0,0.3);
                color: white;
                font-family: monospace;
                margin: 10px 0;
                min-height: 150px;
            }
            select {
                width: 100%;
                padding: 12px;
                border-radius: 8px;
                border: 2px solid rgba(255,255,255,0.3);
                background: rgba(0,0,0,0.3);
                color: white;
                margin: 10px 0;
            }
            .result {
                background: rgba(0,0,0,0.4);
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                word-break: break-all;
                font-family: monospace;
            }
            .success { color: #4caf50; }
            .error { color: #f44336; }
            .loading { display: none; text-align: center; margin: 20px 0; }
            .spinner {
                border: 5px solid rgba(255,255,255,0.3);
                border-top: 5px solid #bb86fc;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ Facebook Token Extractor</h1>
            <p style="text-align: center; margin-bottom: 30px;">Extract Facebook tokens from cookies</p>
            
            <div id="alert" style="display:none; padding:15px; border-radius:8px; margin-bottom:20px;"></div>
            
            <label><b>Select Token Type:</b></label>
            <select id="tokenType">
                <option value="">-- Select Token Type --</option>
                """ + ''.join([f'<option value="{opt}">{opt}</option>' for opt in TOKEN_OPTIONS]) + """
            </select>
            
            <label><b>Facebook Cookie:</b></label>
            <textarea id="cookieInput" placeholder="Paste your Facebook cookie here..."></textarea>
            
            <button class="btn" onclick="extractToken()">🔑 Extract Token</button>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Extracting token...</p>
            </div>
            
            <div id="result" class="result" style="display:none;">
                <h3>Extracted Token:</h3>
                <div id="tokenOutput"></div>
                <button class="btn" onclick="copyToken()" style="margin-top:15px;">📋 Copy Token</button>
            </div>
            
            <div style="margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <h3>📖 How to use:</h3>
                <ol style="margin-left: 20px; margin-top: 10px;">
                    <li>Select a token type from dropdown</li>
                    <li>Paste Facebook cookie in text area</li>
                    <li>Click "Extract Token" button</li>
                    <li>Copy and use the token</li>
                </ol>
            </div>
        </div>
        
        <script>
            let currentToken = '';
            
            function showAlert(message, type = 'error') {
                const alert = document.getElementById('alert');
                alert.textContent = message;
                alert.style.display = 'block';
                alert.style.background = type === 'success' ? 'rgba(76,175,80,0.2)' : 'rgba(244,67,54,0.2)';
                alert.style.border = type === 'success' ? '1px solid #4caf50' : '1px solid #f44336';
                alert.style.color = type === 'success' ? '#a5d6a7' : '#ef9a9a';
                
                setTimeout(() => {
                    alert.style.display = 'none';
                }, 5000);
            }
            
            async function extractToken() {
                const tokenType = document.getElementById('tokenType').value;
                const cookie = document.getElementById('cookieInput').value.trim();
                
                if (!tokenType) {
                    showAlert('Please select a token type');
                    return;
                }
                
                if (!cookie) {
                    showAlert('Please enter Facebook cookie');
                    return;
                }
                
                // Show loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                try {
                    const response = await fetch('/api/extract', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            token_type: tokenType,
                            cookie: cookie
                        })
                    });
                    
                    const data = await response.json();
                    
                    // Hide loading
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.success) {
                        currentToken = data.token;
                        document.getElementById('tokenOutput').textContent = currentToken;
                        document.getElementById('tokenOutput').className = 'success';
                        document.getElementById('result').style.display = 'block';
                        showAlert('Token extracted successfully!', 'success');
                    } else {
                        document.getElementById('tokenOutput').textContent = 'Error: ' + data.error;
                        document.getElementById('tokenOutput').className = 'error';
                        document.getElementById('result').style.display = 'block';
                        showAlert(data.error);
                    }
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('tokenOutput').textContent = 'Network error: ' + error.message;
                    document.getElementById('tokenOutput').className = 'error';
                    document.getElementById('result').style.display = 'block';
                    showAlert('Network error: ' + error.message);
                }
            }
            
            async function copyToken() {
                if (!currentToken) {
                    showAlert('No token to copy');
                    return;
                }
                
                try {
                    await navigator.clipboard.writeText(currentToken);
                    showAlert('Token copied to clipboard!', 'success');
                } catch (error) {
                    showAlert('Failed to copy token');
                }
            }
            
            // Auto-focus cookie input
            document.addEventListener('DOMContentLoaded', function() {
                document.getElementById('cookieInput').focus();
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/extract', methods=['POST'])
def extract():
    try:
        data = request.get_json()
        token_type = data.get('token_type', '')
        cookie = data.get('cookie', '')
        
        if not token_type or not cookie:
            return jsonify({
                'success': False,
                'error': 'Token type and cookie are required'
            })
        
        if token_type not in TOKEN_OPTIONS:
            return jsonify({
                'success': False,
                'error': 'Invalid token type'
            })
        
        # Call external API
        params = {'type': token_type, 'cookie': cookie}
        url = f"{API_URL}?{urllib.parse.urlencode(params)}"
        
        response = requests.get(url, timeout=30)
        response_data = response.json()
        
        token = find_token(response_data)
        
        if token:
            return jsonify({
                'success': True,
                'token': token,
                'token_type': token_type
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Token not found in response',
                'response': response_data
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/health')
def health():
    return jsonify({
        'status': 'online',
        'service': 'Facebook Token Extractor',
        'options': len(TOKEN_OPTIONS)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
