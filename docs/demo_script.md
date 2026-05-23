# Demo Script for Presentation (5 Minutes)

## Pre-requisites (Before you start)
1. Have Docker Desktop running.
2. Have the vulnerable environment running (`docker-compose up -d`).
3. Have Python `venv` activated in two terminal windows (Terminal 1 for exploit, Terminal 2 for validation).
4. Have a browser window open to `http://localhost:8080`.

---

## Minute 1: Problem Statement & Introduction
*(Speaker: Team Member 1)*
**Action:** Show the browser window pointing to `http://localhost:8080`.

**Script:**
"Hello everyone, we are Team [Name]. Today, we're demonstrating Web Cache Poisoning via Host Header Injection. Our project focuses on the Cloud-Native domain, specifically targeting the caching layer (like Nginx or a CDN). The core problem is this: web applications often sit behind caches to improve performance. The cache stores responses based on specific parameters, usually the URL path. However, if the backend application dynamically generates content using un-keyed parameters—like the HTTP `Host` header—an attacker can poison the cache. The impact? Subsequent legitimate users receive the attacker's payload, served directly by our own trusted infrastructure."

---

## Minute 2: High-Level Architecture
*(Speaker: Team Member 2)*
**Action:** Open `docs/architecture_explanation.md` (or a slide showing the diagram).

**Script:**
"Looking at our architecture, we have a typical setup: an Nginx Edge Proxy sitting in front of a Flask backend, both containerized using Docker.
When a request comes in, Nginx checks if it has a cached response for that specific URI. If not, it forwards the request to Flask. 
In our vulnerable configuration, Nginx uses *only* the URI path as the cache key. But our Flask app uses the incoming `Host` header to generate links, such as the source for an analytics tracker. This disconnect between the cache key and the application logic is what we will exploit."

---

## Minute 3: Live Exploit
*(Speaker: Team Member 3)*
**Action:** Go to Terminal 1. Run the exploit script.

**Script:**
"Let's see this in action. First, observe our normal page loading a script from `localhost`.
Now, I'll run our custom exploit tool. We target our local lab and inject a malicious Host header: `evil-hacker.com`."
*(Run command: `python exploit/exploit.py -t http://localhost:8080 -m evil-hacker.com`)*
"The script primes the cache, then sends the poisoned payload. It verifies the response. As you can see, the exploit succeeded. 
Now, let's look at the impact on a victim."
*(Action: Refresh the browser window at `http://localhost:8080`)*
"I am now a normal user, making a normal request. Because the cache is poisoned, the infrastructure serves me the malicious response. My browser is now trying to load the tracker script from `evil-hacker.com`. We have compromised the infrastructure."

---

## Minute 4: Mitigation & Remediation
*(Speaker: Team Member 4)*
**Action:** Go to Terminal 2 (or a code editor) and show `nginx_secure.conf`.

**Script:**
"To mitigate this, we don't fix the application code; we fix the infrastructure configuration. 
First, we must normalize the cache key. In our secure Nginx config, we change `proxy_cache_key $uri` to `proxy_cache_key $http_host$uri`. Now, responses for different hosts are cached separately.
Second, we implement strict header validation. We explicitly define `server_name` and use the validated `$host` variable when proxying, rather than blindly trusting the client's `$http_host`. Finally, we add a default server block to drop requests with unrecognized hosts entirely."

---

## Minute 5: Validation, Impact & Future Work
*(Speaker: Team Member 5)*
**Action:** Apply mitigation (copy secure config over vulnerable and restart docker) and run validation script in Terminal 2.

**Script:**
"Let's validate our fix."
*(Run command to swap configs: `Copy-Item .\nginx\nginx_secure.conf -Destination .\nginx\nginx_vulnerable.conf -Force` then `docker-compose restart nginx`)*
*(Run command: `python tests/validate.py -t http://localhost:8080 -m evil-hacker.com`)*
"Our automated validation test confirms the server is now secure. The cache poisoning fails, and the victim receives safe content.
This aligns with MITRE ATT&CK T1584, Compromise Infrastructure. While this lab is a simplified model, this exact misconfiguration affects major CDNs and enterprise deployments globally. For future work, we would integrate Web Application Firewall (WAF) signatures to detect anomalous Host headers before they even reach the caching layer. Thank you."
