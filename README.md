# Web Cache Poisoning via Host Header Injection

## Objective
The objective of this project is to demonstrate Web Cache Poisoning via Host Header Injection, aligning with the MITRE ATT&CK technique T1584 (Compromise Infrastructure). It provides a local lab environment with a vulnerable Nginx caching layer and a Flask backend, an exploitation tool, and a secure configuration to mitigate the vulnerability.

## Architecture Type
Cloud-Native (Simulated with Docker/Nginx/Flask).

## Security Issue Explained
Web Cache Poisoning occurs when an application processes input from an attacker and includes it in a cached response. If the caching mechanism doesn't include that input in its "cache key" (the unique identifier for a cached page), the poisoned response is served to subsequent legitimate users.

In this specific scenario, the Nginx cache uses only the URL path (`$uri`) as the cache key. However, the backend Flask application uses the `Host` HTTP header to dynamically generate links (e.g., to a tracking script). An attacker can send a request with a malicious `Host` header. Nginx caches the resulting page (which now contains a link to the attacker's script) under the standard URL path. When a normal user requests that same path, Nginx serves the poisoned cached page, causing the user's browser to execute the attacker's script.

## Why Cache Poisoning is Dangerous
- **Mass Exploitation:** A single request from an attacker can compromise thousands of users who subsequently visit the cached page.
- **Difficult to Detect:** The payload is delivered by the legitimate server (from its cache), making it bypass many client-side and network-level security controls.
- **Persistent:** The vulnerability remains active until the cache expires or is manually purged.

## Real-World Relevance
Modern web architectures heavily rely on Content Delivery Networks (CDNs) and reverse proxies (like Nginx, Varnish, Fastly, Cloudflare) to improve performance. Misconfigurations in how these layers define cache keys relative to how backend applications handle HTTP headers (especially the often-overlooked `Host` header) frequently lead to cache poisoning vulnerabilities in production environments.

## Enterprise DevSecOps Features
To demonstrate an understanding of industry standards, this repository includes several enterprise-grade features beyond the core exploit:
- **Cloud-Native IaC:** A `terraform/` directory containing AWS CloudFront configurations demonstrating how to apply this mitigation to cloud infrastructure.
- **CI/CD Security Pipelines:** GitHub Actions (`.github/workflows`) configured for Static Application Security Testing (SAST) using Bandit and container vulnerability scanning using Trivy.
- **SOC SIEM Dashboard:** A web-based Presenter Dashboard that simulates a Security Operations Center, featuring live Nginx access logs and real-time Chart.js traffic analytics to visualize blocked attacks.
- **Enterprise Build Tools:** A `Makefile` for streamlined environment setup and execution.

## Setup Instructions

### Prerequisites
- Windows OS (CMD or PowerShell)
- Docker Desktop installed and running
- Python 3.10+ installed

### 1. Python Virtual Environment Setup

Open PowerShell or CMD in the project root directory (`c:\Users\Thoshan\Desktop\cyber\cache_poisoning_project`).

```powershell
# Create the virtual environment
python -m venv venv

# Activate it (PowerShell)
.\venv\Scripts\Activate.ps1

# OR Activate it (CMD)
venv\Scripts\activate.bat

# Install required packages
pip install -r requirements.txt
```

### 2. Starting the Lab Environment

Ensure Docker Desktop is running. In your terminal:

```powershell
# Build and start the containers in detached mode
docker-compose up --build -d
```

The vulnerable application is now accessible at `http://localhost:8080`.

## Execution Guide

You can run this demo in two ways: **Web Mode (Recommended for presentations)** or **Terminal Mode**.

---

### 🟢 Method A: Web Mode (Presenter Dashboard)

We have included a dedicated Presenter Dashboard to make running the demo incredibly smooth during a hackathon.

1. **Start the Control Panel:**
   Ensure your virtual environment is active, then run:
   ```powershell
   python control_panel.py
   ```
2. **Open the Dashboard:**
   Open your browser and navigate to `http://localhost:9090`.
3. **Run the Demo:**
   - Click **Open Victim Browser** to open `http://localhost:8080` in a new tab. Note the normal tracker URL.
   - Go back to the dashboard and click **Run Cache Poisoning Exploit**. Watch the terminal output in the browser!
   - Refresh the Victim Browser (`http://localhost:8080`) to see the stunning red UI indicating the cache is poisoned!
   - Click **Apply Secure Config & Restart Nginx** to deploy the mitigation.
   - Click **Run Validation Test** to prove the server is now secure.

---

### 🔴 Method B: Terminal Mode

#### 1. Verify Normal Behavior
Open a browser and navigate to `http://localhost:8080`. You should see the CDN Insights Dashboard. Notice the "Detected Host" is `localhost:8080` and the script source points to `http://localhost:8080/assets/tracker.js`.

### 2. Run the Exploit

Ensure your virtual environment is active.

```powershell
# Run the exploit script
python exploit\exploit.py -t http://localhost:8080 -m evil-hacker.com
```

The script will:
1. Check if the target is alive.
2. Send requests with the injected `Host: evil-hacker.com` header.
3. Simulate a victim request to verify the cache was poisoned.

### 3. Verify Poisoning (Manual)
Refresh your browser at `http://localhost:8080`. You should now see the "Detected Host" is `evil-hacker.com` and the script source is `http://evil-hacker.com/assets/tracker.js`. **The cache is poisoned.**

### 4. Apply Mitigation

We will swap the vulnerable Nginx configuration for the secure one.

```powershell
# Edit docker-compose.yml (or run these commands)
# We need to change the volume mount for nginx.

# Stop the current containers
docker-compose down

# Overwrite the vulnerable config with the secure one inside the container context
# For demo purposes, we can just replace the file content directly in the repo
Copy-Item .\nginx\nginx_secure.conf -Destination .\nginx\nginx_vulnerable.conf -Force

# Restart the containers
docker-compose up -d
```

*(Note: The `nginx_secure.conf` includes the `$http_host` in the `proxy_cache_key` and explicitly defines `server_name`)*

### 5. Validate Mitigation

Run the validation script:

```powershell
python tests\validate.py -t http://localhost:8080 -m test-hacker.com
```

The test should confirm that the mitigation is active and poisoning fails.

## MITRE ATT&CK Mapping
- **Tactic:** Resource Development (TA0042) / Initial Access (TA0001) depending on payload.
- **Technique:** T1584 - Compromise Infrastructure
- **Relevance:** By poisoning the cache, the attacker is compromising the infrastructure (the caching layer) to serve malicious content to victims, essentially turning the organization's own CDN against its users.

## Troubleshooting
- **Docker Port Conflicts:** If port 8080 is in use, change it in `docker-compose.yml` (e.g., `"8081:80"`) and update the target URL in the scripts.
- **Exploit Fails (Target not caching):** Ensure Nginx is running properly. Sometimes the first few requests might bypass cache. The script attempts retries.
- **Venv Activation Fails:** Ensure execution policies allow scripts in PowerShell (`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`).
