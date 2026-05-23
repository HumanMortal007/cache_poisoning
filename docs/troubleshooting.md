# Troubleshooting Guide

This guide addresses common issues encountered when setting up or running the Web Cache Poisoning lab.

## Docker Issues

### 1. Port Conflicts (Address already in use)
*   **Error:** `Bind for 0.0.0.0:8080 failed: port is already allocated`
*   **Cause:** Another application (like another web server or a previous Docker container) is using port 8080.
*   **Solution:** Open `docker-compose.yml`. Under the `nginx` service, change the port mapping from `"8080:80"` to another available port, for example, `"8081:80"`. Remember to use this new port in the exploit script (`-t http://localhost:8081`).

### 2. Containers Won't Start or Exit Immediately
*   **Error:** Containers show as 'Exited' when running `docker ps -a`.
*   **Solution:** Check the container logs to identify the issue.
    *   For Flask: `docker logs cdn_flask_backend`
    *   For Nginx: `docker logs cdn_nginx_edge`
    *   A common cause is a syntax error if you manually edited the Python or Nginx configuration files.

### 3. "Cannot connect to the Docker daemon"
*   **Error:** Docker commands fail with daemon connection errors.
*   **Solution:** Ensure Docker Desktop is installed, running, and has finished its startup sequence. You should see the Docker icon in the system tray indicating it is running.

## Python / Script Issues

### 1. "python: command not found" or "python is not recognized"
*   **Cause:** Python is not installed or not added to your system's PATH.
*   **Solution:** Download and install Python 3.10+ from python.org. During installation, ensure the checkbox **"Add Python to PATH"** is checked.

### 2. Virtual Environment (venv) Activation Fails
*   **Error (PowerShell):** `...cannot be loaded because running scripts is disabled on this system.`
*   **Solution:** Windows restricts running PowerShell scripts by default. Open PowerShell as Administrator and run:
    `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
    Then, try activating the venv again.

### 3. ModuleNotFoundError (e.g., "No module named 'requests'")
*   **Cause:** The required Python packages are not installed in the active virtual environment.
*   **Solution:**
    1. Ensure your virtual environment is active (you should see `(venv)` in your prompt).
    2. Run: `pip install -r requirements.txt`

## Exploit / Lab Behavior Issues

### 1. Exploit Fails (Target not caching)
*   **Symptom:** The exploit script reports that the cache status is `MISS` or `BYPASS` repeatedly.
*   **Cause:** The Nginx cache might need a moment to initialize, or the first request might bypass the cache.
*   **Solution:**
    1. The script has built-in retries.
    2. Manually browse to `http://localhost:8080` a few times to ensure the cache is primed.
    3. Run the exploit script again.

### 2. Victim Request Shows Normal Content (Cache not poisoned)
*   **Symptom:** The exploit script says successful, but when you visit the page in a browser, you see the normal `localhost` domain, not the malicious one.
*   **Cause:** You likely requested the page *before* running the exploit. The cache stored the *legitimate* response and is serving it to you. The cache is valid for 10 minutes.
*   **Solution:**
    1. Wait 10 minutes for the cache to expire (not ideal for a demo).
    2. **Faster Solution:** Restart the Nginx container to clear its in-memory cache state.
       `docker-compose restart nginx`
    3. Run the exploit script *first*, before simulating the victim.

### 3. Validation Script Fails
*   **Symptom:** You swapped to `nginx_secure.conf`, but the validation script still says the server is vulnerable.
*   **Cause:** The Nginx container did not reload its configuration.
*   **Solution:** You must restart the Nginx container after replacing the configuration file for the changes to take effect.
    `docker-compose restart nginx`

### 4. Flask Application Errors (Internal Server Error)
*   **Symptom:** Browsing to the target URL returns a 500 error.
*   **Solution:** Check the Flask application logs located in the `logs/app.log` directory on your host machine (this directory is mapped to the container). Look for Python traceback errors to identify code issues.
