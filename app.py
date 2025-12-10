from flask import Flask, request, jsonify
import requests
import json
import urllib.parse
import os
import re

app = Flask(__name__)

# Token options from your original script
TOKEN_OPTIONS = [
    "EAAAAU", "EAAD", "EAAAAAY", "EAADYP", "EAAD6V7", "EAAC2SPKT",
    "EAAGOfO", "EAAVB", "EAAC4", "EAACW5F", "EAAB", "EAAQ",
    "EAAGNO4", "EAAH", "EAAC", "EAAClA", "EAATK", "EAAI7",
]

API_URL = "https://adidaphat.site/facebook/tokentocookie"

def find_token_in_response(response_text):
    """
    Find Facebook token in API response using multiple methods
    """
    # Method 1: Try to parse as JSON first
    try:
        data = json.loads(response_text)
        
        # Recursive search in JSON
        def search_in_json(obj):
            if isinstance(obj, dict):
                # Check common token keys
                for key in ['token', 'access_token', 'Token', 'accessToken', 'AccessToken']:
                    if key in obj and isinstance(obj[key], str) and obj[key].startswith('EA'):
                        return obj[key]
                
                # Search in values
                for value in obj.values():
                    result = search_in_json(value)
                    if result:
                        return result
                        
            elif isinstance(obj, list):
                for item in obj:
                    result = search_in_json(item)
                    if result:
                        return result
            return None
        
        token = search_in_json(data)
        if token:
            return token
    except:
        pass
    
    # Method 2: Regex patterns for Facebook tokens
    token_patterns = [
        r'EAA[UADQCIHKYNW]\w{30,}',  # Common Facebook tokens
        r'EAAB\w{30,}',
        r'EAAC\w{30,}',
        r'EAAD\w{30,}',
        r'EAAE\w{30,}',
        r'EAAF\w{30,}',
        r'EAAG\w{30,}',
        r'EAAH\w{30,}',
        r'EAAI\w{30,}',
        r'EAAJ\w{30,}',
        r'EAAK\w{30,}',
        r'EAAL\w{30,}',
        r'EAAM\w{30,}',
        r'EAAN\w{30,}',
        r'EAAO\w{30,}',
        r'EAAP\w{30,}',
        r'EAAQ\w{30,}',
        r'EAAR\w{30,}',
        r'EAAS\w{30,}',
        r'EAAT\w{30,}',
        r'EAAU\w{30,}',
        r'EAAV\w{30,}',
        r'EAAW\w{30,}',
        r'EAAX\w{30,}',
        r'EAAY\w{30,}',
        r'EAAZ\w{30,}',
        r'access_token":"([^"]+)"',  # JSON format
        r"'token':\s*'([^']+)'",     # Python dict format
        r'"token":\s*"([^"]+)"',     # JSON format
    ]
    
    for pattern in token_patterns:
        matches = re.findall(pattern, response_text)
        if matches:
            token = matches[0] if isinstance(matches[0], str) else matches[0][0] if matches[0] else None
            if token and token.startswith('EA'):
                return token
    
    # Method 3: Look for any long string starting with EA
    all_strings = re.findall(r'EA[A-Za-z0-9]{30,}', response_text)
    for token in all_strings:
        if len(token) > 30:  # Facebook tokens are usually long
            return token
    
    return None

# SIMPLE HTML PAGE
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
                transition: all 0.3s;
            }
            .btn:hover { 
                background: #9c64f7; 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(156, 100, 247, 0.3);
            }
            .btn-secondary {
                background: #03dac6;
                margin-top: 10px;
            }
            .btn-secondary:hover {
                background: #00b8a9;
            }
            textarea {
                width: 100%;
                padding: 15px;
                border-radius: 8px;
                border: 2px solid rgba(255,255,255,0.3);
                background: rgba(0,0,0,0.3);
                color: white;
                font-family: 'Consolas', monospace;
                margin: 10px 0;
                min-height: 150px;
                font-size: 14px;
            }
            textarea:focus {
                outline: none;
                border-color: #bb86fc;
                box-shadow: 0 0 0 3px rgba(187, 134, 252, 0.2);
            }
            select {
                width: 100%;
                padding: 12px;
                border-radius: 8px;
                border: 2px solid rgba(255,255,255,0.3);
                background: rgba(0,0,0,0.3);
                color: white;
                margin: 10px 0;
                font-size: 16px;
            }
            .result {
                background: rgba(0,0,0,0.4);
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                word-break: break-all;
                font-family: 'Consolas', monospace;
                font-size: 14px;
                line-height: 1.6;
            }
            .success { 
                color: #4caf50; 
                border-left: 4px solid #4caf50;
                padding-left: 15px;
            }
            .error { 
                color: #f44336; 
                border-left: 4px solid #f44336;
                padding-left: 15px;
            }
            .warning {
                color: #ff9800;
                border-left: 4px solid #ff9800;
                padding-left: 15px;
            }
            .loading { 
                display: none; 
                text-align: center; 
                margin: 20px 0; 
            }
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
            .alert {
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: none;
                animation: fadeIn 0.3s;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .alert-success {
                background: rgba(76,175,80,0.2);
                border: 1px solid #4caf50;
                color: #a5d6a7;
            }
            .alert-error {
                background: rgba(244,67,54,0.2);
                border: 1px solid #f44336;
                color: #ef9a9a;
            }
            .alert-info {
                background: rgba(33,150,243,0.2);
                border: 1px solid #2196f3;
                color: #90caf9;
            }
            .info-box {
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 8px;
                margin-top: 30px;
            }
            .info-box h3 {
                color: #bb86fc;
                margin-bottom: 15px;
            }
            .info-box ol {
                margin-left: 20px;
                line-height: 1.8;
            }
            .info-box li {
                margin-bottom: 8px;
            }
            .token-info {
                background: rgba(76,175,80,0.1);
                padding: 15px;
                border-radius: 8px;
                margin-top: 15px;
                border-left: 4px solid #4caf50;
            }
            .token-info p {
                margin: 5px 0;
            }
            .copy-btn {
                background: #03dac6;
                color: #000;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin-top: 15px;
                transition: all 0.3s;
            }
            .copy-btn:hover {
                background: #00b8a9;
                transform: translateY(-2px);
            }
            .copy-btn.copied {
                background: #4caf50;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Facebook Token Extractor</h1>
            <p style="text-align: center; margin-bottom: 30px; opacity: 0.9;">
                Extract Facebook Access Tokens from Cookies - 18 Token Types Supported
            </p>
            
            <div id="alert" class="alert"></div>
            
            <div style="margin-bottom: 25px;">
                <label style="display: block; margin-bottom: 8px; color: #bb86fc; font-weight: bold;">
                    📝 Select Token Type:
                </label>
                <select id="tokenType">
                    <option value="">-- Choose Token Type --</option>
                    """ + ''.join([f'<option value="{opt}">{opt}</option>' for opt in TOKEN_OPTIONS]) + """
                </select>
            </div>
            
            <div style="margin-bottom: 25px;">
                <label style="display: block; margin-bottom: 8px; color: #bb86fc; font-weight: bold;">
                    🍪 Facebook Cookie:
                </label>
                <textarea 
                    id="cookieInput" 
                    placeholder="Paste your Facebook cookie here...

Example format:
c_user=100012345678901
xs=35:AbCdEfGhIjKlMnOp:2:1700000000:-1:-1
fr=0AbCdEfGhIjKlMnOp.AWbCdEfG
datr=AbCdEfGhIjKlMnOp
sb=AbCdEfGhIjKlMnOp

Copy full cookie from Chrome/Firefox:
1. Open Facebook → Press F12
2. Go to Application → Cookies
3. Copy all values"
                    rows="8"
                ></textarea>
                
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <button class="btn-secondary" onclick="pasteFromClipboard()" style="flex: 1;">
                        📋 Paste from Clipboard
                    </button>
                    <button class="btn-secondary" onclick="clearInput()" style="flex: 1; background: #f44336;">
                        🗑️ Clear
                    </button>
                    <button class="btn-secondary" onclick="testSample()" style="flex: 1; background: #ff9800;">
                        🧪 Test Sample
                    </button>
                </div>
            </div>
            
            <button class="btn" onclick="extractToken()">
                ⚡ Extract Token
            </button>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Connecting to API... Please wait</p>
                <p style="font-size: 0.9rem; opacity: 0.7; margin-top: 5px;">
                    This may take 10-30 seconds
                </p>
            </div>
            
            <div id="result" class="result" style="display:none;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="color: #bb86fc;">Extracted Token:</h3>
                    <button class="copy-btn" onclick="copyToken()" id="copyBtn">
                        📋 Copy Token
                    </button>
                </div>
                <div id="tokenOutput" class="success"></div>
                <div id="tokenInfo"></div>
                
                <button class="btn-secondary" onclick="newExtraction()" style="width: 100%; margin-top: 20px;">
                    🔄 New Extraction
                </button>
            </div>
            
            <div class="info-box">
                <h3>📖 How to Get Facebook Cookie:</h3>
                <ol>
                    <li><strong>Open Facebook</strong> in Chrome or Firefox browser</li>
                    <li><strong>Press F12</strong> to open Developer Tools</li>
                    <li>Go to <strong>"Application"</strong> tab (or "Storage" in Firefox)</li>
                    <li>In left sidebar, expand <strong>"Cookies"</strong> → <strong>"https://www.facebook.com"</strong></li>
                    <li>Select and copy <strong>ALL</strong> cookie values (right-click → Copy)</li>
                    <li><strong>Paste</strong> the full cookie in the text area above</li>
                </ol>
                
                <div style="margin-top: 20px; padding: 15px; background: rgba(255,152,0,0.1); border-radius: 5px;">
                    <h4 style="color: #ff9800; margin-bottom: 10px;">⚠️ Important Notes:</h4>
                    <ul style="margin-left: 20px;">
                        <li>Make sure you're logged into Facebook</li>
                        <li>Copy ALL cookies, not just one</li>
                        <li>Token extraction success depends on cookie validity</li>
                        <li>Different token types work for different purposes</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <script>
            let currentToken = '';
            
            function showAlert(message, type = 'error', duration = 5000) {
                const alert = document.getElementById('alert');
                alert.textContent = message;
                alert.className = `alert alert-${type}`;
                alert.style.display = 'block';
                
                setTimeout(() => {
                    alert.style.display = 'none';
                }, duration);
            }
            
            async function pasteFromClipboard() {
                try {
                    const text = await navigator.clipboard.readText();
                    document.getElementById('cookieInput').value = text;
                    showAlert('✅ Cookie pasted from clipboard!', 'success');
                } catch (error) {
                    showAlert('❌ Unable to read clipboard. Please paste manually.', 'error');
                }
            }
            
            function clearInput() {
                document.getElementById('cookieInput').value = '';
                document.getElementById('cookieInput').focus();
                showAlert('Cleared input field', 'info', 2000);
            }
            
            function testSample() {
                const sampleCookie = `c_user=100012345678901
xs=35:AbCdEfGhIjKlMnOp:2:1700000000:-1:-1
fr=0AbCdEfGhIjKlMnOp.AWbCdEfG
datr=AbCdEfGhIjKlMnOp
sb=AbCdEfGhIjKlMnOp
wd=1920x939`;
                
                document.getElementById('cookieInput').value = sampleCookie;
                showAlert('✅ Sample cookie loaded for testing!', 'success');
            }
            
            async function extractToken() {
                const tokenType = document.getElementById('tokenType').value;
                const cookie = document.getElementById('cookieInput').value.trim();
                
                // Validation
                if (!tokenType) {
                    showAlert('❌ Please select a token type from the dropdown!', 'error');
                    document.getElementById('tokenType').focus();
                    return;
                }
                
                if (!cookie) {
                    showAlert('❌ Please enter Facebook cookie in the text area!', 'error');
                    document.getElementById('cookieInput').focus();
                    return;
                }
                
                // Check if cookie looks valid
                if (!cookie.includes('c_user=') || !cookie.includes('xs=')) {
                    showAlert('⚠️ Cookie may be incomplete. Make sure it includes c_user and xs values.', 'info');
                }
                
                // Show loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                try {
                    console.log('Sending request to API...');
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
                    
                    console.log('Response received:', response.status);
                    const data = await response.json();
                    console.log('Response data:', data);
                    
                    // Hide loading
                    document.getElementById('loading').style.display = 'none';
                    
                    if (data.success) {
                        currentToken = data.token;
                        document.getElementById('tokenOutput').textContent = currentToken;
                        document.getElementById('tokenOutput').className = 'success';
                        
                        // Show token info
                        const tokenInfo = document.getElementById('tokenInfo');
                        tokenInfo.innerHTML = `
                            <div class="token-info">
                                <p><strong>✅ Token extracted successfully!</strong></p>
                                <p>Type: <strong>${data.token_type}</strong></p>
                                <p>Length: <strong>${currentToken.length} characters</strong></p>
                                <p>Starts with: <strong>${currentToken.substring(0, 10)}...</strong></p>
                                <p>${data.message || 'Ready to use'}</p>
                            </div>
                        `;
                        
                        document.getElementById('result').style.display = 'block';
                        showAlert('🎉 Token extracted successfully! Click "Copy Token" to use it.', 'success');
                        
                        // Scroll to result
                        document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
                    } else {
                        document.getElementById('tokenOutput').textContent = data.error || 'Unknown error';
                        document.getElementById('tokenOutput').className = 'error';
                        
                        // Show debug info if available
                        const tokenInfo = document.getElementById('tokenInfo');
                        tokenInfo.innerHTML = `
                            <div style="background: rgba(244,67,54,0.1); padding: 15px; border-radius: 8px; margin-top: 15px;">
                                <p><strong>❌ Extraction Failed</strong></p>
                                <p>Error: ${data.error}</p>
                                ${data.response ? `<p style="margin-top: 10px; font-size: 12px; opacity: 0.8;">API Response: ${JSON.stringify(data.response).substring(0, 200)}...</p>` : ''}
                            </div>
                        `;
                        
                        document.getElementById('result').style.display = 'block';
                        showAlert(data.error || 'Failed to extract token', 'error');
                    }
                } catch (error) {
                    console.error('Extraction error:', error);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('tokenOutput').textContent = 'Network Error: ' + error.message;
                    document.getElementById('tokenOutput').className = 'error';
                    document.getElementById('result').style.display = 'block';
                    showAlert('🌐 Network error: ' + error.message, 'error');
                }
            }
            
            async function copyToken() {
                if (!currentToken) {
                    showAlert('No token to copy!', 'error');
                    return;
                }
                
                try {
                    await navigator.clipboard.writeText(currentToken);
                    
                    // Visual feedback
                    const copyBtn = document.getElementById('copyBtn');
                    copyBtn.textContent = '✅ Copied!';
                    copyBtn.classList.add('copied');
                    
                    showAlert('✅ Token copied to clipboard!', 'success');
                    
                    setTimeout(() => {
                        copyBtn.textContent = '📋 Copy Token';
                        copyBtn.classList.remove('copied');
                    }, 2000);
                } catch (error) {
                    showAlert('❌ Failed to copy token. Please copy manually.', 'error');
                }
            }
            
            function newExtraction() {
                document.getElementById('cookieInput').value = '';
                document.getElementById('result').style.display = 'none';
                document.getElementById('cookieInput').focus();
                showAlert('Ready for new extraction!', 'info', 2000);
            }
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Ctrl+Enter to extract token
                if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault();
                    extractToken();
                }
                
                // Esc to clear
                if (e.key === 'Escape') {
                    clearInput();
                }
            });
            
            // Auto-focus on page load
            document.addEventListener('DOMContentLoaded', function() {
                document.getElementById('cookieInput').focus();
                
                // Test API connection
                fetch('/health')
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server status:', data);
                    })
                    .catch(error => {
                        console.warn('Health check failed:', error);
                    });
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/extract', methods=['POST'])
def extract():
    try:
        data = request.get_json()
        token_type = data.get('token_type', '').strip()
        cookie = data.get('cookie', '').strip()
        
        if not token_type:
            return jsonify({
                'success': False,
                'error': 'Token type is required'
            })
        
        if token_type not in TOKEN_OPTIONS:
            return jsonify({
                'success': False,
                'error': f'Invalid token type. Must be one of: {", ".join(TOKEN_OPTIONS[:5])}...'
            })
        
        if not cookie:
            return jsonify({
                'success': False,
                'error': 'Cookie is required'
            })
        
        print(f"Extracting token type: {token_type}")
        print(f"Cookie length: {len(cookie)} characters")
        
        # Prepare API request
        params = {'type': token_type, 'cookie': cookie}
        url = f"{API_URL}?{urllib.parse.urlencode(params)}"
        
        print(f"Calling API: {url[:100]}...")
        
        try:
            # Call external API with timeout
            response = requests.get(url, timeout=30)
            print(f"API Response Status: {response.status_code}")
            
            # Get response text
            response_text = response.text
            print(f"Response length: {len(response_text)} characters")
            print(f"First 200 chars: {response_text[:200]}")
            
            # Try to extract token using multiple methods
            token = find_token_in_response(response_text)
            
            if token:
                print(f"✅ Token found: {token[:50]}...")
                return jsonify({
                    'success': True,
                    'token': token,
                    'token_type': token_type,
                    'message': 'Token extracted successfully',
                    'length': len(token)
                })
            else:
                print("❌ No token found in response")
                
                # Try to parse as JSON to show helpful error
                try:
                    error_data = json.loads(response_text)
                    error_msg = error_data.get('error', error_data.get('message', 'Unknown error'))
                    return jsonify({
                        'success': False,
                        'error': f'API Error: {error_msg}',
                        'response': error_data
                    })
                except:
                    # If not JSON, return raw response snippet
                    return jsonify({
                        'success': False,
                        'error': 'Token not found in API response',
                        'response': response_text[:500] if response_text else 'Empty response'
                    })
                    
        except requests.exceptions.Timeout:
            print("❌ API request timeout")
            return jsonify({
                'success': False,
                'error': 'API request timeout. Please try again.'
            })
        except requests.exceptions.RequestException as e:
            print(f"❌ API request error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'API Error: {str(e)}'
            })
            
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server Error: {str(e)}'
        })

@app.route('/health')
def health():
    return jsonify({
        'status': 'online',
        'service': 'Facebook Token Extractor',
        'options': len(TOKEN_OPTIONS),
        'version': '2.0',
        'message': 'Server is running. Use /api/extract to extract tokens.'
    })

@app.route('/api/test')
def test():
    """Test endpoint to check API connectivity"""
    try:
        test_response = requests.get(API_URL + "?type=EAAAAU&cookie=test", timeout=10)
        return jsonify({
            'api_status': 'reachable',
            'status_code': test_response.status_code,
            'response_preview': test_response.text[:200]
        })
    except Exception as e:
        return jsonify({
            'api_status': 'unreachable',
            'error': str(e)
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
