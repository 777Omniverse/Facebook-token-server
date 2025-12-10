import json
import urllib.parse
import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# HTML Template embedded in the Python file
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Token Extractor</title>
    <style>
        :root {
            --primary: #1877f2;
            --secondary: #42b72a;
            --dark: #18191a;
            --gray: #242526;
            --light: #e4e6eb;
            --success: #31a24c;
            --danger: #f02849;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #0c2461 0%, #1e3799 100%);
            color: var(--light);
            min-height: 100vh;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 40px 20px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 15px;
            background: linear-gradient(45deg, #1877f2, #00b2ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 2px 10px rgba(24, 119, 242, 0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .badge {
            display: inline-block;
            background: var(--secondary);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            margin: 10px;
        }
        
        /* Main Content */
        .main-content {
            display: grid;
            grid-template-columns: 1fr;
            gap: 30px;
        }
        
        @media (min-width: 992px) {
            .main-content {
                grid-template-columns: 2fr 1fr;
            }
        }
        
        /* Card */
        .card {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        /* Form Elements */
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: #00b2ff;
            font-size: 1.1rem;
        }
        
        .label-icon {
            margin-right: 10px;
        }
        
        /* Token Grid */
        .token-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .token-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 15px 10px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        
        .token-btn:hover {
            background: rgba(24, 119, 242, 0.3);
            border-color: var(--primary);
            transform: translateY(-2px);
        }
        
        .token-btn.active {
            background: rgba(24, 119, 242, 0.4);
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(24, 119, 242, 0.3);
        }
        
        /* Textarea */
        .cookie-input {
            width: 100%;
            min-height: 150px;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.3);
            color: white;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 1rem;
            resize: vertical;
            transition: border-color 0.3s;
        }
        
        .cookie-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(24, 119, 242, 0.2);
        }
        
        /* Buttons */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 16px 32px;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, #00b2ff 100%);
            color: white;
            width: 100%;
        }
        
        .btn-primary:hover {
            background: linear-gradient(135deg, #166fe5 0%, #0099e6 100%);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(24, 119, 242, 0.3);
        }
        
        .btn-primary:disabled {
            background: #666;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            margin: 5px;
        }
        
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .btn-icon {
            margin-right: 10px;
        }
        
        /* Action Buttons */
        .action-buttons {
            display: flex;
            gap: 15px;
            margin-top: 15px;
        }
        
        /* Loading */
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            width: 60px;
            height: 60px;
            border: 5px solid rgba(255, 255, 255, 0.1);
            border-top: 5px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Result */
        .result-container {
            display: none;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .token-box {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 12px;
            padding: 25px;
            font-family: 'Consolas', 'Monaco', monospace;
            word-break: break-all;
            white-space: pre-wrap;
            border: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 1.1rem;
            line-height: 1.8;
            position: relative;
            min-height: 120px;
        }
        
        .token-success {
            color: var(--success);
            border-left: 4px solid var(--success);
        }
        
        .token-error {
            color: var(--danger);
            border-left: 4px solid var(--danger);
        }
        
        /* Alert */
        .alert {
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 25px;
            display: none;
            animation: slideIn 0.3s;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .alert-success {
            background: rgba(49, 162, 76, 0.15);
            border: 1px solid var(--success);
            color: #a5d6a7;
        }
        
        .alert-error {
            background: rgba(240, 40, 73, 0.15);
            border: 1px solid var(--danger);
            color: #ef9a9a;
        }
        
        .alert-info {
            background: rgba(24, 119, 242, 0.15);
            border: 1px solid var(--primary);
            color: #90caf9;
        }
        
        /* Selected Token */
        .selected-token {
            background: rgba(24, 119, 242, 0.2);
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
            font-weight: bold;
            font-size: 1.2rem;
            border: 2px solid var(--primary);
        }
        
        /* Info Box */
        .info-box {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 25px;
            margin-top: 20px;
        }
        
        .info-box h3 {
            color: #00b2ff;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }
        
        .info-box ol, .info-box ul {
            margin-left: 20px;
            margin-bottom: 15px;
        }
        
        .info-box li {
            margin-bottom: 10px;
        }
        
        .warning {
            background: rgba(240, 40, 73, 0.1);
            border: 1px solid var(--danger);
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        /* Status */
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .status-online {
            background: var(--success);
            color: white;
        }
        
        .status-offline {
            background: var(--danger);
            color: white;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 30px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 15px;
        }
        
        .footer-link {
            color: #00b2ff;
            text-decoration: none;
            transition: opacity 0.3s;
        }
        
        .footer-link:hover {
            opacity: 0.8;
            text-decoration: underline;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            .header {
                padding: 25px 15px;
            }
            
            .header h1 {
                font-size: 2.2rem;
            }
            
            .token-grid {
                grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
            }
            
            .action-buttons {
                flex-direction: column;
            }
            
            .result-header {
                flex-direction: column;
                gap: 15px;
                align-items: flex-start;
            }
        }
        
        @media (max-width: 480px) {
            .token-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .card {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🔐 Facebook Token Extractor</h1>
            <p>Extract Facebook Access Tokens from Browser Cookies</p>
            <div class="badge">18 Token Types Supported</div>
            <div style="margin-top: 15px;">
                <span class="status status-online" id="status-indicator">Checking...</span>
            </div>
        </div>

        <!-- Alert -->
        <div id="alert" class="alert"></div>

        <div class="main-content">
            <!-- Left Column: Main Form -->
            <div>
                <div class="card">
                    <div class="form-group">
                        <label><span class="label-icon">🔑</span> Select Token Type</label>
                        <div class="selected-token" id="selected-token-display">
                            Click on a token type below
                        </div>
                        <div class="token-grid" id="token-grid">
                            <!-- Token buttons will be loaded here -->
                        </div>
                    </div>

                    <div class="form-group">
                        <label><span class="label-icon">🍪</span> Facebook Cookie</label>
                        <textarea 
                            id="cookie-input" 
                            class="cookie-input" 
                            placeholder="Paste your Facebook cookie here...
Example: c_user=1000...; xs=35:abc...; fr=0abc...; datr=abc...

How to get cookie:
1. Open Facebook in Chrome/Firefox
2. Press F12 for Developer Tools
3. Go to Application/Storage → Cookies
4. Copy the entire cookie string"
                        ></textarea>
                        
                        <div class="action-buttons">
                            <button onclick="pasteFromClipboard()" class="btn btn-secondary">
                                📋 Paste from Clipboard
                            </button>
                            <button onclick="clearCookieInput()" class="btn btn-secondary">
                                🗑️ Clear
                            </button>
                            <button onclick="testWithSample()" class="btn btn-secondary">
                                🧪 Test with Sample
                            </button>
                        </div>
                    </div>

                    <button id="extract-btn" onclick="extractToken()" class="btn btn-primary">
                        ⚡ Extract Token
                    </button>

                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <p>Connecting to API...</p>
                        <p style="font-size: 0.9rem; opacity: 0.7; margin-top: 10px;">
                            This may take up to 30 seconds
                        </p>
                    </div>
                </div>

                <!-- Results -->
                <div class="result-container" id="result-container">
                    <div class="card">
                        <div class="result-header">
                            <h2 style="color: #00b2ff;">✅ Extracted Token</h2>
                            <div>
                                <button onclick="copyToken()" id="copy-btn" class="btn btn-secondary">
                                    📋 Copy Token
                                </button>
                                <button onclick="resetForm()" class="btn btn-secondary">
                                    🔄 New Extraction
                                </button>
                            </div>
                        </div>
                        
                        <div class="token-box" id="token-box">
                            Token will appear here...
                        </div>
                        
                        <div id="token-info" style="margin-top: 20px;"></div>
                    </div>
                </div>
            </div>

            <!-- Right Column: Instructions -->
            <div>
                <div class="card">
                    <h3 style="color: #00b2ff; margin-bottom: 20px;">📖 How to Use</h3>
                    
                    <div class="info-box">
                        <h4>Step-by-Step Guide:</h4>
                        <ol>
                            <li><strong>Get Facebook Cookie:</strong>
                                <ul style="margin-left: 15px; margin-top: 5px;">
                                    <li>Login to Facebook in browser</li>
                                    <li>Open Developer Tools (F12)</li>
                                    <li>Go to Application → Cookies</li>
                                    <li>Copy all cookie values</li>
                                </ul>
                            </li>
                            <li><strong>Select Token Type:</strong> Choose from 18 token types</li>
                            <li><strong>Paste Cookie:</strong> Paste into the text area</li>
                            <li><strong>Extract Token:</strong> Click "Extract Token" button</li>
                            <li><strong>Use Token:</strong> Copy and use the extracted token</li>
                        </ol>
                    </div>
                    
                    <div class="info-box">
                        <h4>🛡️ Token Types:</h4>
                        <p>Different token types have different permissions:</p>
                        <ul>
                            <li><strong>EAAAAU:</strong> Standard Access Token</li>
                            <li><strong>EAAD:</strong> Basic Authentication</li>
                            <li><strong>EAADYP:</strong> Page Access</li>
                            <li><strong>EAAGOfO:</strong> Business Manager</li>
                            <li>... and 14 more types</li>
                        </ul>
                    </div>
                    
                    <div class="warning">
                        <h4>⚠️ Important Notes:</h4>
                        <ul>
                            <li>Never share your tokens with anyone</li>
                            <li>Tokens expire after 1-2 hours</li>
                            <li>Use only for educational purposes</li>
                            <li>Respect Facebook's Terms of Service</li>
                        </ul>
                    </div>
                </div>
                
                <div class="card" style="margin-top: 20px;">
                    <h3 style="color: #00b2ff; margin-bottom: 15px;">📊 API Status</h3>
                    <div id="api-status">
                        <p>Checking API connectivity...</p>
                    </div>
                    <button onclick="checkApiStatus()" class="btn btn-secondary" style="margin-top: 10px;">
                        🔄 Refresh Status
                    </button>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Facebook Token Extractor Tool © 2023</p>
            <p>Deployed on Render.com | Version 2.0</p>
            <div class="footer-links">
                <a href="#" onclick="viewAllTokens()" class="footer-link">View All Token Types</a>
                <a href="#" onclick="checkHealth()" class="footer-link">Server Health</a>
                <a href="#" onclick="refreshPage()" class="footer-link">Refresh Page</a>
            </div>
        </div>
    </div>

    <script>
        // ========== CONSTANTS ==========
        const TOKEN_TYPES = [
            "EAAAAU", "EAAD", "EAAAAAY", "EAADYP", "EAAD6V7", "EAAC2SPKT",
            "EAAGOfO", "EAAVB", "EAAC4", "EAACW5F", "EAAB", "EAAQ",
            "EAAGNO4", "EAAH", "EAAC", "EAAClA", "EAATK", "EAAI7"
        ];
        
        const TOKEN_DESCRIPTIONS = {
            "EAAAAU": "Standard Access Token",
            "EAAD": "Basic Authentication Token",
            "EAAAAAY": "Extended Token",
            "EAADYP": "Page Access Token",
            "EAAD6V7": "Application Token",
            "EAAC2SPKT": "Graph API Token",
            "EAAGOfO": "Business Manager Token",
            "EAAVB": "Video Streaming Token",
            "EAAC4": "Ads API Token",
            "EAACW5F": "Marketing API Token",
            "EAAB": "Basic Auth Token",
            "EAAQ": "Query Token",
            "EAAGNO4": "Notification Token",
            "EAAH": "High Security Token",
            "EAAC": "Commerce Token",
            "EAAClA": "Live Streaming Token",
            "EAATK": "Analytics Tracking Token",
            "EAAI7": "Instagram API Token"
        };
        
        // ========== STATE ==========
        let selectedToken = '';
        let extractedToken = '';
        
        // ========== DOM ELEMENTS ==========
        const elements = {
            tokenGrid: document.getElementById('token-grid'),
            selectedTokenDisplay: document.getElementById('selected-token-display'),
            cookieInput: document.getElementById('cookie-input'),
            extractBtn: document.getElementById('extract-btn'),
            loading: document.getElementById('loading'),
            resultContainer: document.getElementById('result-container'),
            tokenBox: document.getElementById('token-box'),
            tokenInfo: document.getElementById('token-info'),
            copyBtn: document.getElementById('copy-btn'),
            alert: document.getElementById('alert'),
            statusIndicator: document.getElementById('status-indicator'),
            apiStatus: document.getElementById('api-status')
        };
        
        // ========== INITIALIZATION ==========
        document.addEventListener('DOMContentLoaded', function() {
            initializeTokenGrid();
            checkServerHealth();
            checkApiStatus();
        });
        
        // ========== TOKEN GRID ==========
        function initializeTokenGrid() {
            elements.tokenGrid.innerHTML = '';
            
            TOKEN_TYPES.forEach(token => {
                const button = document.createElement('button');
                button.className = 'token-btn';
                button.innerHTML = `
                    <div style="font-weight: bold; font-size: 1.1rem;">${token}</div>
                    <div style="font-size: 0.85rem; opacity: 0.8; margin-top: 5px;">
                        ${TOKEN_DESCRIPTIONS[token] || 'Facebook Token'}
                    </div>
                `;
                
                button.addEventListener('click', () => {
                    selectToken(token, button);
                });
                
                elements.tokenGrid.appendChild(button);
            });
            
            // Select first token by default
            if (TOKEN_TYPES.length > 0) {
                selectToken(TOKEN_TYPES[0], elements.tokenGrid.firstChild);
            }
        }
        
        function selectToken(token, button) {
            // Remove active class from all buttons
            document.querySelectorAll('.token-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to selected button
            button.classList.add('active');
            selectedToken = token;
            
            // Update display
            elements.selectedTokenDisplay.innerHTML = `
                Selected: <strong>${token}</strong> - ${TOKEN_DESCRIPTIONS[token] || 'Facebook Token'}
            `;
            
            showAlert(`Selected token type: ${token}`, 'info', 2000);
        }
        
        // ========== FORM FUNCTIONS ==========
        async function pasteFromClipboard() {
            try {
                const text = await navigator.clipboard.readText();
                elements.cookieInput.value = text;
                showAlert('Cookie pasted from clipboard!', 'success');
            } catch (error) {
                showAlert('Unable to read clipboard. Please paste manually.', 'error');
            }
        }
        
        function clearCookieInput() {
            elements.cookieInput.value = '';
            elements.cookieInput.focus();
            showAlert('Cookie input cleared!', 'info');
        }
        
        function testWithSample() {
            const sampleCookie = 'c_user=100012345678901; xs=35:AbCdEfGhIjKlMnOp:2:1700000000:-1:-1; fr=0AbCdEfGhIjKlMnOp.AWbCdEfG; datr=AbCdEfGhIjKlMnOp; sb=AbCdEfGhIjKlMnOp';
            elements.cookieInput.value = sampleCookie;
            showAlert('Sample cookie loaded for testing!', 'info');
        }
        
        function resetForm() {
            elements.cookieInput.value = '';
            elements.resultContainer.style.display = 'none';
            elements.cookieInput.focus();
            showAlert('Ready for new extraction!', 'info');
        }
        
        // ========== TOKEN EXTRACTION ==========
        async function extractToken() {
            // Validation
            if (!selectedToken) {
                showAlert('Please select a token type first!', 'error');
                return;
            }
            
            const cookie = elements.cookieInput.value.trim();
            
            if (!cookie) {
                showAlert('Please enter your Facebook cookie!', 'error');
                elements.cookieInput.focus();
                return;
            }
            
            if (cookie.length < 50) {
                showAlert('Cookie seems too short. Please check and try again.', 'error');
                return;
            }
            
            // Show loading
            elements.loading.style.display = 'block';
            elements.extractBtn.disabled = true;
            elements.resultContainer.style.display = 'none';
            
            try {
                const response = await fetch('/api/extract', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        token_type: selectedToken,
                        cookie: cookie
                    })
                });
                
                const data = await response.json();
                
                // Hide loading
                elements.loading.style.display = 'none';
                elements.extractBtn.disabled = false;
                
                if (data.success) {
                    // Display token
                    extractedToken = data.token;
                    elements.tokenBox.textContent = extractedToken;
                    elements.tokenBox.className = 'token-box token-success';
                    
                    // Display token info
                    elements.tokenInfo.innerHTML = `
                        <div style="background: rgba(49, 162, 76, 0.1); padding: 20px; border-radius: 10px;">
                            <p style="color: #31a24c; font-weight: bold;">
                                ✅ Token extracted successfully!
                            </p>
                            <p>Type: <strong>${data.token_type}</strong></p>
                            <p>Length: <strong>${data.length} characters</strong></p>
                            <p style="margin-top: 10px; font-size: 0.9rem;">
                                ${data.message || 'Ready to use'}
                            </p>
                        </div>
                    `;
                    
                    elements.resultContainer.style.display = 'block';
                    showAlert('Token extracted successfully!', 'success');
                    
                    // Scroll to result
                    elements.resultContainer.scrollIntoView({ behavior: 'smooth' });
                } else {
                    // Display error
                    elements.tokenBox.textContent = `Error: ${data.error}`;
                    elements.tokenBox.className = 'token-box token-error';
                    
                    if (data.api_response) {
                        elements.tokenBox.textContent += `\n\nAPI Response:\n${JSON.stringify(data.api_response, null, 2)}`;
                    }
                    
                    elements.tokenInfo.innerHTML = `
                        <div style="background: rgba(240, 40, 73, 0.1); padding: 20px; border-radius: 10px;">
                            <p style="color: #f02849; font-weight: bold;">
                                ❌ Failed to extract token
                            </p>
                            <p>Error: ${data.error}</p>
                        </div>
                    `;
                    
                    elements.resultContainer.style.display = 'block';
                    showAlert(data.error, 'error');
                }
                
            } catch (error) {
                // Hide loading
                elements.loading.style.display = 'none';
                elements.extractBtn.disabled = false;
                
                // Display network error
                elements.tokenBox.textContent = `Network Error: ${error.message}`;
                elements.tokenBox.className = 'token-box token-error';
                elements.resultContainer.style.display = 'block';
                
                showAlert(`Network error: ${error.message}`, 'error');
                console.error('Extraction error:', error);
            }
        }
        
        // ========== COPY TOKEN ==========
        async function copyToken() {
            if (!extractedToken) {
                showAlert('No token to copy!', 'error');
                return;
            }
            
            try {
                await navigator.clipboard.writeText(extractedToken);
                
                // Visual feedback
                const originalText = elements.copyBtn.innerHTML;
                elements.copyBtn.innerHTML = '✅ Copied!';
                elements.copyBtn.style.background = '#31a24c';
                
                showAlert('Token copied to clipboard!', 'success');
                
                setTimeout(() => {
                    elements.copyBtn.innerHTML = originalText;
                    elements.copyBtn.style.background = '';
                }, 2000);
            } catch (error) {
                showAlert('Failed to copy token. Please copy manually.', 'error');
            }
        }
        
        // ========== API STATUS ==========
        async function checkApiStatus() {
            elements.apiStatus.innerHTML = '<p>Checking API status...</p>';
            
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                
                elements.apiStatus.innerHTML = `
                    <p><strong>Status:</strong> <span class="status status-online">Online</span></p>
                    <p><strong>Service:</strong> ${data.service || 'Facebook Token Tool'}</p>
                    <p><strong>Version:</strong> ${data.version || '1.0.0'}</p>
                    <p><strong>Token Types:</strong> ${data.options_count || 18}</p>
                `;
                
                elements.statusIndicator.textContent = 'Online';
                elements.statusIndicator.className = 'status status-online';
                
            } catch (error) {
                elements.apiStatus.innerHTML = `
                    <p><strong>Status:</strong> <span class="status status-offline">Offline</span></p>
                    <p>Unable to connect to API server</p>
                `;
                
                elements.statusIndicator.textContent = 'Offline';
                elements.statusIndicator.className = 'status status-offline';
            }
        }
        
        async function checkServerHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                console.log('Server health:', data);
            } catch (error) {
                console.warn('Health check failed:', error);
            }
        }
        
        // ========== UTILITY FUNCTIONS ==========
        function showAlert(message, type = 'info', duration = 5000) {
            elements.alert.textContent = message;
            elements.alert.className = `alert alert-${type}`;
            elements.alert.style.display = 'block';
            
            if (duration > 0) {
                setTimeout(() => {
                    elements.alert.style.display = 'none';
                }, duration);
            }
        }
        
        function viewAllTokens() {
            const tokenList = TOKEN_TYPES.map(token => 
                `${token}: ${TOKEN_DESCRIPTIONS[token] || 'Facebook Token'}`
            ).join('\n');
            
            alert(`All Token Types:\n\n${tokenList}`);
        }
        
        function checkHealth() {
            fetch('/health')
                .then(res => res.json())
                .then(data => {
                    alert(`Server Health:\n\n${JSON.stringify(data, null, 2)}`);
                })
                .catch(error => {
                    alert(`Health check failed: ${error.message}`);
                });
        }
        
        function refreshPage() {
            location.reload();
        }
        
        // ========== KEYBOARD SHORTCUTS ==========
        document.addEventListener('keydown', function(e) {
            // Ctrl+Enter to extract token
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                extractToken();
            }
            
            // Escape to clear
            if (e.key === 'Escape') {
                clearCookieInput();
            }
            
            // Number keys 1-9 to select tokens
            if (e.key >= '1' && e.key <= '9') {
                const index = parseInt(e.key) - 1;
                if (index < TOKEN_TYPES.length) {
                    const token = TOKEN_TYPES[index];
                    const button = document.querySelectorAll('.token-btn')[index];
                    if (button) {
                        selectToken(token, button);
                    }
                }
            }
        });
    </script>
</body>
</html>
'''

# Token Options (same as your original script)
TOKEN_OPTIONS = [
    "EAAAAU", "EAAD", "EAAAAAY", "EAADYP", "EAAD6V7", "EAAC2SPKT",
    "EAAGOfO", "EAAVB", "EAAC4", "EAACW5F", "EAAB", "EAAQ",
    "EAAGNO4", "EAAH", "EAAC", "EAAClA", "EAATK", "EAAI7",
]

API_BASE_URL = "https://adidaphat.site/facebook/tokentocookie"

def find_token_in_data(data):
    """Recursively search for 'token' in nested data (same as original)"""
    if isinstance(data, dict):
        if 'token' in data:
            return data['token']
        for value in data.values():
            result = find_token_in_data(value)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_token_in_data(item)
            if result:
                return result
    return None

# ========== FLASK ROUTES ==========

@app.route('/')
def home():
    """Serve the main HTML page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'Facebook Token Extractor',
        'version': '2.0',
        'options_count': len(TOKEN_OPTIONS),
        'message': 'Server is running'
    })

@app.route('/api/extract', methods=['POST'])
def extract_token():
    """Extract token from Facebook cookie (same logic as original)"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        token_type = data.get('token_type', '').strip()
        cookie = data.get('cookie', '').strip()
        
        # Validate inputs
        if not token_type:
            return jsonify({
                'success': False,
                'error': 'Token type is required'
            }), 400
            
        if token_type not in TOKEN_OPTIONS:
            return jsonify({
                'success': False,
                'error': 'Invalid token type selected'
            }), 400
            
        if not cookie:
            return jsonify({
                'success': False,
                'error': 'Cookie is required'
            }), 400
        
        # Prepare API request (same as original script)
        params = {'type': token_type, 'cookie': cookie}
        query_string = urllib.parse.urlencode(params)
        api_url = f"{API_BASE_URL}?{query_string}"
        
        # Call external API with timeout
        import requests
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'error': 'Request timeout. Please try again.'
            }), 504
        except requests.exceptions.RequestException as e:
            return jsonify({
                'success': False,
                'error': f'API error: {str(e)}'
            }), 502
        
        # Parse response
        try:
            api_response = response.json()
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': 'Invalid response from API',
                'raw_response': response.text[:500]
            }), 500
        
        # Extract token (same function as original)
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
            # Try pattern matching for tokens
            import re
            response_text = json.dumps(api_response)
            
            # Common Facebook token patterns
            token_patterns = [
                r'EAA[UADQCIHKYNW]\w{30,}',
                r'EAAB\w{30,}',
                r'EAAC\w{30,}',
                r'EAAD\w{30,}',
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
            'error': f'Internal error: {str(e)}'
        }), 500

@app.route('/api/options')
def get_options():
    """Get available token options"""
    return jsonify({
        'success': True,
        'options': TOKEN_OPTIONS,
        'count': len(TOKEN_OPTIONS)
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ========== MAIN APPLICATION ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
