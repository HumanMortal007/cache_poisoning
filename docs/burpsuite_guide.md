# Burp Suite Integration Guide

While the automated Python scripts (`exploit.py` and `validate.py`) are great for a smooth presentation, using **Burp Suite** is highly recommended if you want to manually prove to the judges that the vulnerability exists at the raw HTTP protocol level. 

Yes, **you will see the exact same results** in Burp Suite as you do with the Python scripts. In fact, showing it in Burp Suite often earns bonus points in hackathons because it demonstrates a deep understanding of HTTP mechanics.

## How to use Burp Suite for this Demo

### 1. Setup
1. Ensure the vulnerable environment is running (`docker-compose up -d`).
2. Open Burp Suite (Community Edition is fine).
3. Go to the **Proxy** tab and turn **Intercept On**.
4. Configure your browser to use Burp Suite as its proxy (or use Burp's built-in Chromium browser).

### 2. Identifying Cacheable Endpoints (Deliverable A)
1. Navigate to `http://localhost:8080` in your proxied browser.
2. In Burp Suite, look at the HTTP response. You will see our custom header:
   `X-Cache-Status: MISS` (or `EXPIRED`/`HIT`).
3. Send this request to **Repeater** (`Ctrl+R` or `Cmd+R`).
4. Click "Send" a few times. You will see the `X-Cache-Status` change to `HIT`, proving the endpoint `/` is actively being cached by Nginx.

### 3. Poisoning the Cache (Deliverable B)
1. In the **Repeater** tab, locate the `Host` header.
2. Change it from `Host: localhost:8080` to `Host: evil-hacker.com`.
3. *(Crucial Step)*: You may need to wait for the previous cache to expire, or use the "Clear Cache" button on your Presenter Dashboard (`http://localhost:9090`) to ensure a fresh cache state.
4. Click "Send". 
5. Look at the response in Burp Suite. You will see that the tracker script has changed to `<script src="http://evil-hacker.com/assets/tracker.js"></script>`.

### 4. Demonstrating Victim Impact (Deliverable C)
1. Turn **Intercept Off** in Burp Suite.
2. Open a completely normal, unproxied browser window (like Edge or Chrome Incognito).
3. Navigate to `http://localhost:8080`.
4. You will see the red poisoned UI, and if you inspect the page source, you will see `evil-hacker.com`. This proves that a normal user making a normal request received the poisoned cache payload!

### 5. Verifying the Fix (Deliverable D)
1. Apply the Secure Config from your Presenter Dashboard.
2. Go back to Burp Suite Repeater.
3. Try sending the malicious `Host: evil-hacker.com` request again.
4. You will receive no response! Burp Suite will show a connection error or an empty response because the secure Nginx configuration actively drops connections containing invalid Host headers (returning `444`).
