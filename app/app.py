import logging
from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Configure logging to write to both console and file
log_dir = "/app/logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{log_dir}/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("flask_app")

# HTML Template for the frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CDN Insights Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e2f; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background-color: #2a2a40; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h1 { color: #00d2ff; text-align: center; border-bottom: 2px solid #3a3a5c; padding-bottom: 10px; }
        .info-box { background-color: #3a3a5c; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid #00d2ff; }
        .data-row { display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid #4a4a6c; padding-bottom: 5px; }
        .label { font-weight: bold; color: #a0a0c0; }
        .value { color: #e0e0e0; font-family: monospace; }
        .dynamic-content { background-color: #1e1e2f; padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px dashed #666; }
        .highlight { color: #ff3366; font-weight: bold; }
        .btn { display: inline-block; padding: 10px 20px; background-color: #00d2ff; color: #1e1e2f; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 15px; transition: background-color 0.3s; }
        .btn:hover { background-color: #00b8e6; }
        .footer { margin-top: 30px; text-align: center; color: #777; font-size: 0.9em; }
    </style>
    <!-- VULNERABILITY: Dynamically loading a script based on the Host header -->
    <script src="http://{{ host_header }}/assets/tracker.js"></script>
</head>
<body>
    <div class="container">
        <h1>CDN Insights Dashboard</h1>
        
        <div class="info-box">
            <h3>Environment Information</h3>
            <div class="data-row">
                <span class="label">Server Time:</span>
                <span class="value">{{ timestamp }}</span>
            </div>
            <div class="data-row">
                <span class="label">Requested Path:</span>
                <span class="value">{{ path }}</span>
            </div>
            <div class="data-row">
                <span class="label">Detected Host:</span>
                <span class="value highlight">{{ host_header }}</span>
            </div>
            <div class="data-row">
                <span class="label">Client IP:</span>
                <span class="value">{{ client_ip }}</span>
            </div>
        </div>

        <div class="dynamic-content">
            <h3>Analytics Tracker Status</h3>
            <p>The analytics tracking script is configured to load from your primary domain.</p>
            <p>Current configuration points to: <code>http://{{ host_header }}/assets/tracker.js</code></p>
            <div id="tracker-status">Initializing tracker...</div>
        </div>
        
        <a href="/" class="btn">Refresh Data</a>
    </div>
    
    <div class="footer">
        Powered by CustomCDN Internal Dashboard &copy; 2026
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """
    Main dashboard route. 
    VULNERABILITY: It reads the Host header from the request and reflects it in the response.
    This response will be cached by Nginx based on the URL path ('/').
    """
    # Extract the Host header (the vulnerability)
    host_header = request.headers.get('Host', 'unknown-host')
    client_ip = request.remote_addr
    path = request.path
    
    # Log the request for demonstration
    logger.info(f"Dashboard accessed - IP: {client_ip}, Host Header: {host_header}, Path: {path}")

    return render_template_string(
        HTML_TEMPLATE,
        host_header=host_header,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        path=path,
        client_ip=client_ip
    )

@app.route('/api/health')
def health():
    """Simple un-cached endpoint for health checking"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    # Run on all interfaces, port 5000 inside the container
    app.run(host='0.0.0.0', port=5000, debug=False)
