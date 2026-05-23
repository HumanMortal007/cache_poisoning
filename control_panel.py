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
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            padding: 20px; 
        }

        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
        }

        h1 { 
            text-align: center; 
            color: var(--accent-primary);
            margin-bottom: 20px;
            font-weight: 800;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .panel {
            background: var(--surface-color);
            padding: 20px;
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
            margin-bottom: 10px;
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

        .terminals-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }

        .terminal-wrapper h3 {
            margin: 0 0 10px 0;
            color: var(--accent-info);
            font-size: 1.1rem;
            display: flex;
            justify-content: space-between;
        }
        
        .pulse-dot {
            height: 10px; width: 10px; background-color: var(--accent-danger); border-radius: 50%; display: inline-block;
            animation: pulse 1.5s infinite; margin-right: 5px;
        }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

        .terminal {
            background-color: #000;
            border-radius: 8px;
            padding: 15px;
            height: 350px;
            overflow-y: auto;
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            color: #a8b2d1;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
            border: 1px solid #333;
        }
        
        .terminal-line { margin-bottom: 4px; white-space: pre-wrap; word-break: break-all; }
        .color-green { color: #10b981; }
        .color-red { color: #ef4444; }
        .color-yellow { color: #f59e0b; }
        .color-cyan { color: #06b6d4; }
        .color-purple { color: #a855f7; }
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
                <button class="btn btn-warning" onclick="runCommand('/api/apply_vulnerable')" style="background-color: #64748b; margin-top: 15px;">⏪ Reset to Vulnerable Config</button>
            </div>
        </div>

        <div class="terminals-container">
            <div class="terminal-wrapper">
                <h3>Command Output</h3>
                <div class="terminal" id="terminal-output">
                    <div class="terminal-line color-cyan">System initialized. Waiting for presenter commands...</div>
                </div>
            </div>
            
            <div class="terminal-wrapper">
                <h3><span><span class="pulse-dot"></span> Live Nginx Access Logs (Proof)</span></h3>
                <div class="terminal" id="nginx-logs-output">
                    <div class="terminal-line color-cyan">Connecting to Docker logs...</div>
                </div>
            </div>
        </div>

        <div class="panel" style="margin-top: 20px;">
            <h2>📊 SOC Traffic Analytics (WAF & Cache Status)</h2>
            <div style="height: 250px; width: 100%;">
                <canvas id="trafficChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        function appendOutput(text, isError = false) {
            const terminal = document.getElementById('terminal-output');
            const line = document.createElement('div');
            line.className = 'terminal-line';
            
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

        // Initialize Chart.js
        const ctx = document.getElementById('trafficChart').getContext('2d');
        const trafficChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Normal Requests (200)', 'Cache Hits', 'Blocked Attacks (444)'],
                datasets: [{
                    label: 'Request Events (Last 50 Logs)',
                    data: [0, 0, 0],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.7)', // Blue
                        'rgba(16, 185, 129, 0.7)', // Green
                        'rgba(239, 68, 68, 0.7)'   // Red
                    ],
                    borderColor: [
                        'rgba(59, 130, 246, 1)',
                        'rgba(16, 185, 129, 1)',
                        'rgba(239, 68, 68, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#94a3b8', stepSize: 1 } },
                    x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                },
                plugins: {
                    legend: { labels: { color: '#f8fafc' } }
                }
            }
        });

        // Poll Nginx logs every 2 seconds
        async function fetchLogs() {
            try {
                const response = await fetch('/api/logs');
                const data = await response.json();
                if (data.output) {
                    const terminal = document.getElementById('nginx-logs-output');
                    // Format log lines to highlight malicious hosts and Cache HITs
                    const formattedLogs = data.output.split('\\n').map(line => {
                        if (!line.trim()) return '';
                        let formatted = line;
                        if (line.includes('evil-hacker.com') || line.includes('test-hacker.com')) {
                            formatted = `<span class="color-red">${formatted}</span>`;
                        } else if (line.includes('Cache Status: "HIT"')) {
                            formatted = formatted.replace('Cache Status: "HIT"', 'Cache Status: "<span class="color-green">HIT</span>"');
                        } else if (line.includes(' 444 ')) {
                            formatted = `<span class="color-purple">${formatted} (BLOCKED)</span>`;
                        }
                        return `<div class="terminal-line">${formatted}</div>`;
                    }).join('');
                    
                    // Only update if changed to avoid scrolling jank if possible
                    if (terminal.innerHTML !== formattedLogs) {
                        terminal.innerHTML = formattedLogs;
                        terminal.scrollTop = terminal.scrollHeight;
                    }

                    // Update Chart Data if stats are provided
                    if (data.stats) {
                        trafficChart.data.datasets[0].data = [data.stats.normal, data.stats.hits, data.stats.blocked];
                        trafficChart.update();
                    }
                }
            } catch (err) {
                console.error("Failed to fetch logs:", err);
            }
        }

        setInterval(fetchLogs, 2000);
        fetchLogs();
    </script>
</body>
</html>
"""

def execute_cmd(cmd, cwd=BASE_DIR, success_msg=""):
    """Helper to run shell commands and return output"""
    try:
        result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=15)
        # Combine stdout and stderr
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        
        # Add success message if the command succeeded
        if result.returncode == 0 and success_msg:
            output += f"\n\n[SUCCESS] {success_msg}"
            
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/clear_cache', methods=['POST'])
def clear_cache():
    return execute_cmd("docker exec cdn_nginx_edge rm -rf /var/cache/nginx/my_cache && docker exec cdn_nginx_edge nginx -s reload", success_msg="Cache cleared successfully!")

@app.route('/api/run_exploit', methods=['POST'])
def run_exploit():
    python_exec = os.path.join(BASE_DIR, 'venv', 'Scripts', 'python.exe')
    script_path = os.path.join(BASE_DIR, 'exploit', 'exploit.py')
    # Use unbuffered python to get output nicely if we were streaming, but here we just wait
    return execute_cmd(f"{python_exec} {script_path} -t http://localhost:8080 -m evil-hacker.com", success_msg="Exploit script execution finished.")

@app.route('/api/run_validate', methods=['POST'])
def run_validate():
    python_exec = os.path.join(BASE_DIR, 'venv', 'Scripts', 'python.exe')
    script_path = os.path.join(BASE_DIR, 'tests', 'validate.py')
    return execute_cmd(f"{python_exec} {script_path} -t http://localhost:8080 -m test-hacker.com", success_msg="Validation script execution finished.")

@app.route('/api/apply_secure', methods=['POST'])
def apply_secure():
    cmd = 'copy nginx\\nginx_secure_original.conf nginx\\nginx_vulnerable.conf && docker-compose restart nginx'
    return execute_cmd(cmd, success_msg="Secure configuration applied and Nginx restarted.")

@app.route('/api/apply_vulnerable', methods=['POST'])
def apply_vulnerable():
    cmd = 'copy nginx\\nginx_vulnerable_original.conf nginx\\nginx_vulnerable.conf && docker-compose restart nginx'
    return execute_cmd(cmd, success_msg="Vulnerable configuration applied and Nginx restarted.")

@app.route('/api/logs', methods=['GET'])
def get_logs():
    # Read the last 50 lines from the Nginx access log inside the container
    # We return 15 lines for the terminal, but use all 50 for stats
    result = execute_cmd("docker exec cdn_nginx_edge tail -n 50 /var/log/nginx/access.log")
    
    # Parse stats from the output
    data = result.get_json()
    if 'output' in data:
        lines = data['output'].strip().split('\n')
        # We only want to show the last 15 lines in the terminal view
        terminal_lines = '\n'.join(lines[-15:])
        
        # Calculate stats for the chart from the 50 lines
        normal = sum(1 for line in lines if '" 200 ' in line and 'api/health' not in line)
        hits = sum(1 for line in lines if 'Cache Status: "HIT"' in line)
        blocked = sum(1 for line in lines if ' 444 ' in line)
        
        return jsonify({
            "output": terminal_lines,
            "stats": {"normal": normal, "hits": hits, "blocked": blocked}
        })
    return result

if __name__ == '__main__':
    print("[+] Starting Presenter Dashboard on http://localhost:9090")
    app.run(host='0.0.0.0', port=9090, debug=True)
