# Frequently Asked Questions (Judge Q&A)

**Q1: What is the core difference between a regular XSS and Web Cache Poisoning?**
*Answer:* In regular XSS, the attacker usually needs to trick the victim into clicking a crafted link (Reflected) or the payload is stored directly in the database (Stored). In Cache Poisoning, the payload is injected into the caching layer (infrastructure), which then actively serves the payload to anyone requesting that specific, legitimate URL.

**Q2: Why did you choose Nginx for this lab instead of simulating a commercial CDN?**
*Answer:* Nginx provides the core proxy and caching functionality that all CDNs are built upon. It allows us to transparently show the configuration directives (`proxy_cache_key`, `proxy_set_header`) that cause the vulnerability, making it reproducible and easy to understand in a local Docker environment without requiring paid cloud accounts.

**Q3: How does the application in your lab actually use the Host header?**
*Answer:* The Flask application reads the incoming `Host` header to dynamically build the absolute URL for an analytics tracking script. If the `Host` header is spoofed, the resulting HTML contains a `<script>` tag pointing to an attacker-controlled domain.

**Q4: Why does the vulnerable Nginx config only use the URI as the cache key?**
*Answer:* This is a common default or copy-pasted configuration. Administrators often assume that a specific path (like `/`) always returns the same content, neglecting the fact that backend applications might alter the response based on headers like `Host`, `User-Agent`, or `Accept-Language`.

**Q5: What happens if an attacker sends a malicious Host header to a securely configured server?**
*Answer:* In our mitigated configuration, two things happen. First, the cache key includes the host, so the payload won't poison the cache for legitimate users. Second, Nginx validates the Host against the `server_name` directive. If it doesn't match, Nginx immediately returns a 444 status (Connection Closed) and drops the request before it even reaches the backend.

**Q6: What is MITRE ATT&CK T1584?**
*Answer:* T1584 is "Compromise Infrastructure." Cache poisoning perfectly aligns with this because the attacker isn't compromising the underlying web application code itself; rather, they are compromising the CDN/caching layer infrastructure to distribute their payload.

**Q7: Can this attack be performed blindly, without knowing the application's internal structure?**
*Answer:* Yes. Tools like Param Miner can automatically spray headers against endpoints and check if the reflected responses vary, indicating a potential cache poisoning vector without needing source code access.

**Q8: If the backend application didn't use the Host header, would this vulnerability exist?**
*Answer:* No. Web Cache Poisoning requires a "gadget"—a piece of unkeyed input (like the Host header) that the backend application actively reflects or uses to alter the response. If the backend ignored the Host header, the cached response would be safe regardless of the cache key configuration.

**Q9: Could a Web Application Firewall (WAF) prevent this?**
*Answer:* Yes, a properly configured WAF placed *before* the caching layer could detect and block anomalous Host headers or known malicious payloads in headers. However, if the WAF sits *behind* the cache, it won't prevent the poisoning, as the cache will serve the bad response without consulting the backend WAF.

**Q10: Why didn't you fix the vulnerability in the Python Flask code?**
*Answer:* While we *could* hardcode the domain in the Flask app, fixing it at the infrastructure layer (Nginx) is the architecturally correct approach. It provides a defense-in-depth mechanism that protects the application even if a developer introduces a new reflection vulnerability later. The cache must accurately reflect the uniqueness of the response.

**Q11: Are there other headers besides `Host` that can be abused for cache poisoning?**
*Answer:* Yes. `X-Forwarded-Host`, `X-Forwarded-Scheme`, `User-Agent`, and custom application-specific headers are frequently overlooked when defining cache keys and can be exploited if the backend reflects them.

**Q12: How long does a cache poisoning attack last?**
*Answer:* It lasts until the cache entry expires (defined by `proxy_cache_valid` in Nginx, or `max-age` headers) or until the cache is manually purged by an administrator.

**Q13: What is "Cache Key Normalization"?**
*Answer:* It's the process of defining exactly which parts of an HTTP request (URI, specific headers, query parameters) make a response unique. Proper normalization ensures that variations in these inputs result in separate, isolated cache entries.

**Q14: Can cache poisoning be used for Denial of Service (DoS)?**
*Answer:* Yes. If an attacker poisons the cache with a response that causes errors, redirects to a black hole, or simply serves a blank page, they have effectively caused a DoS for all legitimate users accessing that cached endpoint.

**Q15: How does your exploit script verify that the poisoning was successful?**
*Answer:* The script first sends the payload with the malicious Host header. Then, it sends a completely normal request (simulating a victim). If the response to the normal request contains the malicious host *and* the `X-Cache-Status` header indicates a `HIT`, we know the cache was successfully poisoned.

**Q16: Why use Docker for this project?**
*Answer:* Docker guarantees reproducibility. It ensures that the exact same versions of Nginx, Python, and the application dependencies run consistently across different environments, which is crucial for demonstrating infrastructure-level vulnerabilities reliably.

**Q17: Is this vulnerability common in the wild?**
*Answer:* Extremely common. It frequently appears in bug bounty programs targeting major platforms because modern web stacks involve multiple layers of caching (browser, CDN, reverse proxy, application cache), and synchronizing cache keys across all layers is difficult.

**Q18: What is the significance of the `X-Cache-Status` header in your Nginx config?**
*Answer:* We explicitly added this header to aid in debugging and demonstration. It tells us whether Nginx served the response from the cache (`HIT`), fetched it from the backend (`MISS`), or ignored the cache (`BYPASS`). This is essential for proving the exploit mechanism.

**Q19: How would an attacker monetize this exploit?**
*Answer:* They could inject a malicious JavaScript tracker (like a crypto-miner or keylogger), redirect users to phishing sites to steal credentials, or deface the website for ideological reasons.

**Q20: Why are unkeyed query parameters dangerous?**
*Answer:* If a cache ignores query parameters (e.g., caching `/page?id=1` and `/page?id=2` as the same thing) but the backend application uses them, an attacker can request `/page?malicious=payload`. The cache stores this under `/page`, and all subsequent visitors to `/page` receive the payload.

**Q21: Can you poison a cache with a 404 Not Found response?**
*Answer:* Yes. If an attacker requests a valid page with a header that causes the backend to error or return a 404, and the cache is configured to cache errors (e.g., `proxy_cache_valid 404 1m;`), the attacker can deny access to that valid page.

**Q22: How does the `$host` variable in Nginx differ from `$http_host`?**
*Answer:* `$http_host` is the raw `Host` header sent by the client. `$host` is evaluated in a specific order: the hostname from the request line, then the `Host` header, and finally the `server_name` defined in the Nginx config block. Using `$host` provides a fallback to a known-good configuration if the client header is missing or malformed.

**Q23: What are the limitations of this specific lab setup?**
*Answer:* It doesn't simulate geographic cache distribution (where poisoning one edge node might not affect users routed to a different node), and it doesn't incorporate the complex, layered rule sets found in enterprise CDNs like Akamai or Cloudflare.

**Q24: Could this attack bypass Content Security Policy (CSP)?**
*Answer:* If the CSP allows scripts from the domain the attacker injected, yes. However, if the CSP is strictly defined to only allow scripts from trusted domains, the browser would block the execution of the poisoned script, mitigating the impact (though the cache remains poisoned).

**Q25: In a real-world scenario, who is responsible for preventing this: the developer or the DevOps engineer?**
*Answer:* It's a shared responsibility (DevSecOps). Developers must ensure applications handle unvalidated input securely, and DevOps engineers must ensure infrastructure configurations accurately reflect the application's caching requirements. Communication between the two is key.
