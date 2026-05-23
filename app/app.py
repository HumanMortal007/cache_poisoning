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
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Fira+Code:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --accent-primary: #38bdf8;
            --accent-secondary: #818cf8;
            --glass-bg: rgba(30, 41, 59, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --danger: #ef4444;
        }

        body { 
            font-family: 'Outfit', sans-serif; 
            background-color: var(--bg-color); 
            background-image: 
                radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(129, 140, 248, 0.15) 0px, transparent 50%);
            background-attachment: fixed;
            color: var(--text-main); 
            margin: 0; 
            padding: 40px 20px; 
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .container { 
            width: 100%;
            max-width: 900px; 
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            padding: 40px; 
            border-radius: 24px; 
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); 
            position: relative;
            overflow: hidden;
        }

        .container::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 4px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
        }

        h1 { 
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(to right, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 0;
            margin-bottom: 30px;
            text-align: center; 
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        .card { 
            background: rgba(15, 23, 42, 0.6); 
            padding: 20px; 
            border-radius: 16px; 
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            border-color: rgba(56, 189, 248, 0.2);
        }

        .card h3 {
            font-size: 1.1rem;
            color: var(--accent-primary);
            margin-top: 0;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .data-row { 
            display: flex; 
            flex-direction: column; 
            margin-bottom: 15px; 
        }

        .data-row:last-child { margin-bottom: 0; }

        .label { 
            font-size: 0.85rem;
            font-weight: 600; 
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted); 
            margin-bottom: 4px;
        }

        .value { 
            font-family: 'Fira Code', monospace;
            font-size: 1rem;
            color: var(--text-main); 
            background: rgba(0, 0, 0, 0.3);
            padding: 8px 12px;
            border-radius: 8px;
            word-break: break-all;
        }

        .highlight { 
            color: var(--danger); 
            font-weight: 600; 
            box-shadow: inset 0 0 0 1px rgba(239, 68, 68, 0.3);
            background: rgba(239, 68, 68, 0.1);
        }

        .tracker-card {
            grid-column: 1 / -1;
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
            border-left: 4px solid var(--accent-secondary);
        }

        .tracker-info {
            display: flex;
            align-items: center;
            gap: 15px;
            background: rgba(0,0,0,0.4);
            padding: 15px;
            border-radius: 12px;
            margin-top: 15px;
        }

        .pulse {
            width: 12px;
            height: 12px;
            background-color: var(--accent-primary);
            border-radius: 50%;
            box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.7);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(56, 189, 248, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(56, 189, 248, 0); }
        }

        .btn { 
            display: inline-flex; 
            align-items: center;
            justify-content: center;
            padding: 14px 28px; 
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)); 
            color: #fff; 
            text-decoration: none; 
            border-radius: 12px; 
            font-weight: 600; 
            letter-spacing: 0.02em;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: none;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
        }

        .btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -10px rgba(56, 189, 248, 0.6);
            filter: brightness(1.1);
        }

        .footer { 
            margin-top: 40px; 
            text-align: center; 
            color: var(--text-muted); 
            font-size: 0.9em; 
        }

        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
        }
    </style>
    <!-- VULNERABILITY: Dynamically loading a script based on the Host header -->
    <script src="http://{{ host_header }}/assets/tracker.js"></script>
</head>
<body>
    <div class="container">
        <h1>Global Edge CDN Insights</h1>
        
        <div class="grid">
            <div class="card">
                <h3><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg> Request Diagnostics</h3>
                <div class="data-row">
                    <span class="label">Server Time</span>
                    <span class="value">{{ timestamp }}</span>
                </div>
                <div class="data-row">
                    <span class="label">Requested Path</span>
                    <span class="value">{{ path }}</span>
                </div>
            </div>

            <div class="card">
                <h3><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> Security Context</h3>
                <div class="data-row">
                    <span class="label">Client IP</span>
                    <span class="value">{{ client_ip }}</span>
                </div>
                <div class="data-row">
                    <span class="label">Detected Host Header</span>
                    <span class="value highlight">{{ host_header }}</span>
                </div>
            </div>

            <div class="card tracker-card">
                <h3><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg> Analytics Engine</h3>
                <p style="color: var(--text-muted); margin-bottom: 0; font-size: 0.95rem;">The analytics tracker script is dynamically injected based on the requested domain configuration.</p>
                
                <div class="tracker-info">
                    <div class="pulse" id="pulse-indicator"></div>
                    <div>
                        <div class="label">Active Tracker Source:</div>
                        <div style="font-family: 'Fira Code', monospace; color: var(--accent-primary); margin-top: 4px;" id="tracker-url">
                            http://{{ host_header }}/assets/tracker.js
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <a href="/" class="btn">Refresh Live Data</a>
    </div>
    
    <div class="footer">
        Powered by CustomCDN Enterprise &copy; 2026 | Node: Edge-US-East
    </div>

    <script>
        // Check if the host header looks suspicious to change the pulse color
        const hostHeader = "{{ host_header }}";
        if (hostHeader !== "localhost:8080" && hostHeader !== "localhost") {
            const pulse = document.getElementById('pulse-indicator');
            pulse.style.backgroundColor = 'var(--danger)';
            pulse.style.boxShadow = '0 0 0 0 rgba(239, 68, 68, 0.7)';
            
            // Re-inject keyframes for red pulse
            const style = document.createElement('style');
            style.innerHTML = `
                @keyframes pulse {
                    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
                    70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
                    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
                }
            `;
            document.head.appendChild(style);
        }
    </script>
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
