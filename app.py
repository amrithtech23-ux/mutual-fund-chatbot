import os
import requests
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# --- API CONFIGURATION ---
OPEN_ROUTER_API_KEY = os.getenv('MFKEY2K6', '')
OPEN_ROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL_NAME = 'qwen/qwen-2.5-72b-instruct'

# --- KNOWLEDGE BASE (From demo.txt) ---
KNOWLEDGE_BASE = """
## FOR COMMERCE STUDENTS (12 Topics)
**Focus:** Foundational understanding of mutual funds, investor perspective, and basic investment concepts.
1. **What Are Mutual Funds and How Do They Work?** Understanding pooled investments, NAV calculation, and fund structures.
2. **Types of Mutual Funds:** Equity, debt, hybrid, index, sectoral, and thematic funds explained.
3. **Understanding NAV, AUM, and Expense Ratios:** Key metrics every mutual fund investor should know.
4. **SIP vs. Lump Sum Investing:** When to use systematic investment plans versus one-time investments.
5. **Risk-Return Profiles of Different Fund Categories:** Matching fund types to investor risk tolerance.
6. **Tax Implications of Mutual Fund Investments:** Capital gains, dividend distribution tax, and tax-saving funds (ELSS).
7. **How to Read a Mutual Fund Factsheet:** Interpreting portfolio holdings, performance, and risk metrics.
8. **Direct vs. Regular Plans:** Understanding the impact of distributor commissions on returns.
9. **Exit Loads and Lock-in Periods:** What investors need to know before redeeming fund units.
10. **Fund Performance Benchmarking:** How to compare fund returns against appropriate indices.
11. **The Role of Fund Managers and AMCs:** Understanding who manages your money and how decisions are made.
12. **Building a Diversified Mutual Fund Portfolio:** Basic principles of asset allocation for retail investors.

## FOR MBA FINANCE STUDENTS (13 Topics)
**Focus:** Analytical frameworks, portfolio theory, performance evaluation, and strategic fund selection.
13. **Modern Portfolio Theory and Mutual Fund Construction:** How diversification and correlation drive fund design.
14. **Sharpe Ratio, Alpha, Beta, and Standard Deviation:** Advanced metrics for evaluating fund risk-adjusted performance.
15. **Active vs. Passive Fund Management:** Cost-benefit analysis of outperformance potential versus index tracking.
16. **Factor Investing and Smart Beta Funds:** Understanding value, momentum, quality, and low-volatility strategies.
17. **Style Drift and Manager Consistency:** Analyzing whether fund managers stick to their stated investment mandate.
18. **Sector Rotation and Tactical Asset Allocation:** How fund managers adjust portfolios based on market cycles.
19. **Currency-Hedged International Funds:** Managing FX risk in global equity and debt fund investments.
20. **ESG Integration in Mutual Fund Selection:** Evaluating sustainability criteria alongside financial returns.
21. **Fund of Funds (FoF) Structures:** Analyzing the pros and cons of layered fund investments.
22. **Liquidity Management in Open-End Funds:** How AMCs handle redemption pressures and cash flow mismatches.
23. **Performance Attribution Analysis:** Decomposing fund returns into asset allocation, security selection, and timing effects.
24. **Behavioral Finance and Mutual Fund Flows:** How investor sentiment drives fund inflows/outflows and market impact.
25. **Regulatory Frameworks Governing Mutual Funds:** Understanding SEBI, SEC, UCITS, and other jurisdictional requirements.

## FOR INVESTMENT BANKING ASPIRANTS/STUDENTS (12 Topics)
**Focus:** Practical industry knowledge, career pathways, and operational understanding of the mutual fund ecosystem.
26. **The Mutual Fund Value Chain:** Roles of AMCs, distributors, custodians, registrars, and depositaries.
27. **Fund Distribution Channels:** Understanding the economics of direct, advisor, platform, and institutional sales.
28. **New Fund Offerings (NFOs) – Process and Pitfalls:** How new funds are launched, marketed, and evaluated.
29. **Fund Mergers and Scheme Rationalization:** Why AMCs consolidate schemes and what it means for investors.
30. **Understanding Fund Documentation:** Scheme Information Documents (SID), Key Information Memoranda (KIM), and annual reports.
31. **Mutual Fund Research and Analyst Roles:** What equity/debt analysts at AMCs do and how to prepare for these careers.
32. **Sales and Distribution Careers in Mutual Funds:** Skills needed for relationship management and channel development roles.
33. **Compliance and Operations Roles in AMCs:** Understanding back-office functions, regulatory reporting, and risk controls.
34. **Preparing for Mutual Fund Industry Interviews:** Common technical and behavioral questions for entry-level roles.
35. **Certifications for Mutual Fund Professionals:** NISM, CFA, CAIA, and other credentials that add value.
36. **Building a Mutual Fund Research Portfolio:** How to document fund analysis, model portfolios, and market commentary.
37. **Networking in the Asset Management Industry:** Strategies for connecting with professionals and finding opportunities.

## FOR INVESTMENT BANKING PROFESSIONALS (13 Topics)
**Focus:** Advanced product structuring, market dynamics, strategic implications, and institutional perspectives.
38. **Designing Thematic and Sectoral Fund Products:** Structuring funds around emerging trends like AI, clean energy, or demographics.
39. **Institutional Share Classes and Fee Negotiations:** Customizing terms for pension funds, sovereign wealth funds, and endowments.
40. **Cross-Border Fund Distribution Strategies:** Navigating regulatory approvals, tax treaties, and localization requirements.
41. **Liquidity Tools for Open-End Funds:** Swing pricing, redemption gates, and side pockets for managing stress scenarios.
42. **Derivatives Usage in Mutual Funds:** How futures, options, and swaps enhance returns or manage risk within regulatory limits.
43. **Private Credit and Alternative Mutual Funds:** Structuring liquid alternatives for retail and institutional investors.
44. **Fund Incubation and Track Record Building:** Strategies for launching new strategies with limited historical performance.
45. **M&A in the Asset Management Industry:** Valuation drivers, integration challenges, and synergy realization in AMC deals.
46. **ETF vs. Mutual Fund Product Strategy:** When to launch an ETF versus a traditional open-end fund for a given strategy.
47. **Fee Compression and Business Model Innovation:** How AMCs adapt pricing, scale, and service offerings in competitive markets.
48. **Technology and Data Analytics in Fund Management:** Using AI, alternative data, and quantitative models to enhance investment processes.
49. **Regulatory Arbitrage and Jurisdiction Selection:** Strategic considerations for fund domicile, listing, and distribution.
50. **The Future of Mutual Funds:** Trends in personalization, direct indexing, tokenization, and the evolution of pooled investment vehicles.
"""

SYSTEM_PROMPT = f"""You are a Mutual Fund Chatbot expert designed to help:
- Commerce Students
- MBA Finance Students  
- Investment Banking Aspirants/Students
- Investment Banking Professionals

Knowledge Base (50 Topics):
{KNOWLEDGE_BASE}

Instructions:
1. Provide accurate, detailed responses about mutual funds
2. Tailor complexity based on user's apparent knowledge level
3. Use clear examples and practical insights
4. Format with bullet points and structured formatting
5. Keep responses concise but comprehensive (300-500 words)
6. Maintain professional tone suitable for finance professionals
7. If question is outside mutual fund domain, politely redirect
"""

# 10 Random Suggestion Prompts (Mutual Fund Domain)
SUGGESTION_PROMPTS = [
    "What are the key differences between equity and debt mutual funds?",
    "How do I calculate the NAV of a mutual fund?",
    "Explain SIP and its benefits for long-term investing",
    "What is the Sharpe Ratio and how is it used in fund evaluation?",
    "How does expense ratio impact mutual fund returns?",
    "What are ELSS funds and their tax benefits under Section 80C?",
    "Explain active vs passive fund management strategies",
    "How do I read and interpret a mutual fund factsheet?",
    "What are the risks associated with sectoral mutual funds?",
    "How do fund managers handle liquidity during market crashes?"
]

# --- HTML TEMPLATE (Embedded in app.py) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mutual Fund Chatbot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1100px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        .header {
            text-align: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #4169E1;
        }
        .header h1 { color: #1e3a8a; font-size: 2.2em; margin-bottom: 8px; }
        .header p { color: #666; font-size: 1em; }
        
        .target-audience {
            background: #f0f4ff;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 5px solid #4169E1;
        }
        .target-audience h3 { color: #1e3a8a; margin-bottom: 8px; }
        .target-audience ul {
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .target-audience li {
            background: #4169E1;
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .suggestion-section { margin-bottom: 20px; }
        .suggestion-section h3 {
            color: #1e3a8a;
            margin-bottom: 12px;
            font-size: 1.2em;
        }
        .suggestions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 12px;
            margin-bottom: 15px;
        }
        .suggestion-btn {
            background: #4169E1;
            color: white;
            border: 3px solid #1e3a8a;
            padding: 14px 18px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: bold;
            color: royalblue;
            transition: all 0.3s ease;
            text-align: left;
        }
        .suggestion-btn:hover {
            background: #1e3a8a;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(65, 105, 225, 0.4);
        }
        
        .query-section { margin-bottom: 20px; }
        .query-section label {
            display: block;
            color: #1e3a8a;
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        .query-input {
            width: 100%;
            min-height: 100px;
            padding: 15px;
            border: 3px solid #1e3a8a;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            background: #4169E1;
            color: white;
            resize: vertical;
            font-family: inherit;
        }
        .query-input::placeholder { color: rgba(255,255,255,0.8); }
        .query-input:focus {
            outline: none;
            border-color: #1e3a8a;
            box-shadow: 0 0 0 3px rgba(65, 105, 225, 0.3);
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            margin: 15px 0;
        }
        .submit-btn, .reset-btn {
            padding: 14px 35px;
            font-size: 1.1em;
            font-weight: bold;
            border: 3px solid #1e3a8a;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .submit-btn {
            background: #4169E1;
            color: white;
        }
        .submit-btn:hover {
            background: #1e3a8a;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(65, 105, 225, 0.4);
        }
        .reset-btn {
            background: #dc3545;
            color: white;
        }
        .reset-btn:hover {
            background: #c82333;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(220, 53, 69, 0.4);
        }
        
        .result-section { margin-top: 20px; }
        .result-section label {
            display: block;
            color: #1e3a8a;
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        .result-output {
            width: 100%;
            min-height: 300px;
            padding: 20px;
            border: 3px solid #1e3a8a;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            background: #4169E1;
            color: white;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: white;
            font-style: italic;
        }
        .error {
            background: #dc3545 !important;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
        }
        
        .footer {
            margin-top: 25px;
            text-align: center;
            color: #666;
            font-size: 0.85em;
            padding-top: 15px;
            border-top: 2px solid #ddd;
        }
        
        @media (max-width: 768px) {
            .suggestions-grid { grid-template-columns: 1fr; }
            .button-group { flex-direction: column; }
            .header h1 { font-size: 1.6em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Mutual Fund Chatbot</h1>
            <p>Powered by Qwen 2.5 72B | 50+ Topics | For Finance Professionals & Students</p>
        </div>

        <div class="target-audience">
            <h3>🎯 Target Audience:</h3>
            <ul>
                <li>📈 Commerce Students</li>
                <li>💼 MBA Finance Students</li>
                <li>🚀 Investment Banking Aspirants</li>
                <li>🏦 Investment Banking Professionals</li>
            </ul>
        </div>

        <div class="suggestion-section">
            <h3>💡 Suggested Prompts (Click to use):</h3>
            <div class="suggestions-grid">
                {% for suggestion in suggestions %}
                <button class="suggestion-btn" onclick="useSuggestion('{{ suggestion }}')">
                    {{ suggestion }}
                </button>
                {% endfor %}
            </div>
        </div>

        <div class="query-section">
            <label for="userQuery">📝 Enter Your Mutual Fund Query:</label>
            <textarea 
                id="userQuery" 
                class="query-input" 
                placeholder="Type your question about mutual funds here... Or click any suggestion above."
            ></textarea>
        </div>

        <div class="button-group">
            <button class="submit-btn" onclick="submitQuery()">🚀 Submit Query</button>
            <button class="reset-btn" onclick="resetChat()">🔄 Reset Chat</button>
        </div>

        <div class="result-section">
            <label for="resultOutput">💬 Chatbot Response:</label>
            <div id="resultOutput" class="result-output">Your response will appear here...</div>
        </div>

        <div class="footer">
            <p>50+ Mutual Fund Topics | MIT License | Built with Open Router API</p>
        </div>
    </div>

    <script>
        function useSuggestion(text) {
            document.getElementById('userQuery').value = text;
        }

        async function submitQuery() {
            const query = document.getElementById('userQuery').value.trim();
            const output = document.getElementById('resultOutput');
            
            if (!query) {
                alert('Please enter a query');
                return;
            }

            output.innerHTML = '<div class="loading">⏳ Processing your query... Please wait...</div>';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });

                const data = await response.json();

                if (data.success) {
                    output.textContent = data.response;
                } else {
                    output.innerHTML = '<div class="error">❌ Error: ' + data.error + '</div>';
                }
            } catch (error) {
                output.innerHTML = '<div class="error">❌ Network Error: ' + error.message + '</div>';
            }
        }

        function resetChat() {
            document.getElementById('userQuery').value = '';
            document.getElementById('resultOutput').textContent = 'Your response will appear here...';
        }

        document.getElementById('userQuery').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submitQuery();
            }
        });
    </script>
</body>
</html>
"""

# --- ROUTES ---
@app.route('/')
def index():
    """Render the main chatbot interface"""
    return render_template_string(HTML_TEMPLATE, suggestions=SUGGESTION_PROMPTS)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests and return responses from Qwen model"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Please enter a query',
                'response': ''
            }), 400
        
        # Check if API key is configured
        if not OPEN_ROUTER_API_KEY or OPEN_ROUTER_API_KEY == 'your-api-key-here':
            return jsonify({
                'success': False,
                'error': 'API key not configured. Please set MFKEY2K6 environment variable.',
                'response': 'Error: API key missing. Contact administrator to configure MFKEY2K6.'
            }), 500
        
        # Prepare API request to Open Router
        headers = {
            'Authorization': f'Bearer {OPEN_ROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/your-username/mutual-fund-chatbot',
            'X-Title': 'Mutual Fund Chatbot'
        }
        
        payload = {
            'model': MODEL_NAME,
            'messages': [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_query}
            ],
            'temperature': 0.7,
            'max_tokens': 1000,
            'top_p': 0.9
        }
        
        # Make API call to Open Router
        response = requests.post(
            OPEN_ROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result['choices'][0]['message']['content']
            
            return jsonify({
                'success': True,
                'response': bot_response,
                'query': user_query
            })
        else:
            error_msg = f"API Error: {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', error_msg)
            except:
                pass
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'response': f"Sorry, I encountered an error: {error_msg}. Please try again."
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Request timeout. Please try again.',
            'response': 'The request took too long. Please try your query again.'
        }), 504
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': 'Network error occurred. Please check your connection and try again.'
        }), 503
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': 'An unexpected error occurred. Please try again.'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Mutual Fund Chatbot',
        'model': MODEL_NAME,
        'topics': 50,
        'api_configured': bool(OPEN_ROUTER_API_KEY and OPEN_ROUTER_API_KEY != 'your-api-key-here')
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)