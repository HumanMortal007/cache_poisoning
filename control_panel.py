import os
import subprocess
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hackathon Presenter Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Fira+Code:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --surface-color: #1e293b;
            --accent-primary: #10b981;
            --accent-warning: #f59e0b;
            --accent-danger: #ef4444;
            --accent-info: #3b82f6;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        body { 
            font-family: 'Outfit', sans-serif; 
            background-color: var(--bg-color); 
            color: var(--text-main); 
            margin: 0; 
            padding: 30px; 
        }

        .container { 
            max-width: 1000px; 
            margin: 0 auto; 
        }

        h1 { 
            text-align: center; 
            color: var(--accent-primary);
            margin-bottom: 30px;
            font-weight: 800;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .panel {
            background: var(--surface-color);
            padding: 25px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .panel h2 {
            margin-top: 0;
            border-bottom: 2px solid rgba(255,255,255,0.05);
            padding-bottom: 10px;
            font-size: 1.2rem;
            color: var(--text-muted);
        }

        .btn {
            display: block;
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: none;
            border-radius: 8px;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 1rem;
            color: #fff;
            cursor: pointer;
            transition: transform 0.2s, opacity 0.2s;
        }

        .btn:hover { transform: translateY(-2px); opacity: 0.9; }
        .btn:active { transform: translateY(0); }

        .btn-exploit { background-color: var(--accent-danger); }
        .btn-mitigate { background-color: var(--accent-primary); }
        .btn-reset { background-color: var(--accent-warning); }
        .btn-clear { background-color: var(--accent-info); }

        .terminal {
            background-color: #000;
            border-radius: 8px;
            padding: 15px;
            height: 400px;
            overflow-y: auto;
            font-family: 'Fira Code', monospace;
            font-size: 0.9rem;
            color: #a8b2d1;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
            border: 1px solid #333;
            margin-top: 20px;
        }
        
        .terminal-line { margin-bottom: 4px; white-space: pre-wrap; word-break: break-all; }
        .color-green { color: #10b981; }
        .color-red { color: #ef4444; }
        .color-yellow { color: #f59e0b; }
        .color-cyan { color: #06b6d4; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ Hackathon Presenter Dashboard</h1>
        
        <div class="grid">
            <div class="panel">
                <h2>Phase 1: Exploitation</h2>
                <button class="btn btn-clear" onclick="runCommand('/api/clear_cache')">🧹 1. Clear Nginx Cache</button>
                <button class="btn btn-exploit" onclick="runCommand('/api/run_exploit')">🔥 2. Run Cache Poisoning Exploit</button>
                <a href="http://localhost:8080" target="_blank" class="btn btn-info" style="text-align: center; text-decoration: none; box-sizing: border-box; background-color: #3b82f6;">👀 3. Open Victim Browser (localhost:8080)</a>
            </div>

            <div class="panel">
                <h2>Phase 2: Mitigation</h2>
                <button class="btn btn-mitigate" onclick="runCommand('/api/apply_secure')">🛡️ 4. Apply Secure Config & Restart Nginx</button>
                <button class="btn btn-reset" onclick="runCommand('/api/run_validate')">✅ 5. Run Validation Test</button>
                <button class="btn btn-warning" onclick="runCommand('/api/apply_vulnerable')" style="background-color: #64748b; margin-top: 30px;">⏪ Reset to Vulnerable Config</button>
            </div>
        </div>

        <div class="terminal" id="terminal-output">
            <div class="terminal-line color-cyan">System initialized. Waiting for presenter commands...</div>
        </div>
    </div>

    <script>
        function appendOutput(text, isError = false) {
            const terminal = document.getElementById('terminal-output');
            const line = document.createElement('div');
            line.className = 'terminal-line';
            
            // Simple ANSI color parsing for web terminal
            let formatted = text
                .replace(/\\[0m/g, '</span>')
                .replace(/\\[32m/g, '<span class="color-green">')
                .replace(/\\[31m/g, '<span class="color-red">')
                .replace(/\\[33m/g, '<span class="color-yellow">')
                .replace(/\\[36m/g, '<span class="color-cyan">');
                
            line.innerHTML = formatted;
            if (isError) line.classList.add('color-red');
            terminal.appendChild(line);
            terminal.scrollTop = terminal.scrollHeight;
        }

        async function runCommand(endpoint) {
            appendOutput(`\\n<span class="color-yellow">[*] Executing ${endpoint}...</span>`);
            try {
                const response = await fetch(endpoint, { method: 'POST' });
                const data = await response.json();
                
                if (data.output) {
                    const lines = data.output.split('\\n');
                    lines.forEach(l => appendOutput(l));
                }
                if (data.error) {
                    appendOutput(`Error: ${data.error}`, true);
                }
            } catch (err) {
                appendOutput(`Failed to execute request: ${err}`, true);
            }
        }
    </script>
</body>
</html>
"""

def execute_cmd(cmd, cwd=BASE_DIR):
    """Helper to run shell commands and return output"""
    try:
        result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=15)
        # Combine stdout and stderr
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/clear_cache', methods=['POST'])
def clear_cache():
    return execute_cmd("docker exec cdn_nginx_edge rm -rf /var/cache/nginx/my_cache && docker exec cdn_nginx_edge nginx -s reload")

@app.route('/api/run_exploit', methods=['POST'])
def run_exploit():
    python_exec = os.path.join(BASE_DIR, 'venv', 'Scripts', 'python.exe')
    script_path = os.path.join(BASE_DIR, 'exploit', 'exploit.py')
    # Use unbuffered python to get output nicely if we were streaming, but here we just wait
    return execute_cmd(f"{python_exec} {script_path} -t http://localhost:8080 -m evil-hacker.com")

@app.route('/api/run_validate', methods=['POST'])
def run_validate():
    python_exec = os.path.join(BASE_DIR, 'venv', 'Scripts', 'python.exe')
    script_path = os.path.join(BASE_DIR, 'tests', 'validate.py')
    return execute_cmd(f"{python_exec} {script_path} -t http://localhost:8080 -m test-hacker.com")

@app.route('/api/apply_secure', methods=['POST'])
def apply_secure():
    cmd = 'copy nginx\\nginx_secure_original.conf nginx\\nginx_vulnerable.conf && docker-compose restart nginx'
    return execute_cmd(cmd)

@app.route('/api/apply_vulnerable', methods=['POST'])
def apply_vulnerable():
    cmd = 'copy nginx\\nginx_vulnerable_original.conf nginx\\nginx_vulnerable.conf && docker-compose restart nginx'
    return execute_cmd(cmd)

if __name__ == '__main__':
    print("[+] Starting Presenter Dashboard on http://localhost:9090")
    app.run(host='0.0.0.0', port=9090, debug=True)
