# Architecture Explanation: Cloud-Native Cache Poisoning Lab

## 1. Why Cloud-Native?
The "Cloud-Native" architectural style is prevalent in modern application deployment. It relies heavily on microservices, containerization, and layered infrastructure (API gateways, CDNs, reverse proxies). This lab utilizes Docker to simulate a simplified version of this architecture, making the vulnerability context highly relevant to real-world deployments.

## 2. Component Breakdown
- **Attacker Client:** The entity sending crafted HTTP requests (our Python exploit script).
- **Victim Client:** A legitimate user accessing the application via a standard web browser (simulated by our script/browser).
- **Edge Proxy / Cache (Nginx):** Acts as the entry point. In the real world, this could be Cloudflare, AWS CloudFront, Fastly, or an internal Varnish/Nginx cluster. Its job is to cache static or semi-static content to reduce load on the backend.
- **Backend Application (Flask):** The core business logic. It dynamically generates content based on request parameters and headers.

## 3. High-Level Architecture Diagram
```text
      [ Attacker ]                [ Victim ]
           |                          |
           | (Malicious Host Header)  | (Normal Request)
           v                          v
    +----------------------------------------+
    |           Edge Proxy (Nginx)           |
    |                                        |
    |  Cache Key: / (Vulnerable Config)      |
    |  Cached Data: <script src="evil.com">  |
    +----------------------------------------+
           | (Proxied Request)
           v
    +----------------------------------------+
    |         Backend App (Flask)            |
    |                                        |
    |  Reads Host Header -> evil.com         |
    |  Generates HTML with evil.com          |
    +----------------------------------------+
```

## 4. The Role of Nginx Caching
Nginx is configured as a reverse proxy with caching enabled (`proxy_cache`).
- **Performance:** Caching drastically improves response times.
- **The Pitfall:** Caching mechanisms must uniquely identify requests to serve the correct stored response. This unique identifier is the `cache_key`. If the cache key is too simplistic (e.g., only using the URL path) while the backend generates varied responses based on un-keyed headers (like `Host`), a desynchronization occurs.

## 5. Real-World CDN Relevance
Content Delivery Networks (CDNs) operate on the same principles. They cache content at edge locations worldwide. If a CDN is configured to ignore the `Host` header or specific query parameters when building its cache key, but the origin server uses them, cache poisoning becomes possible on a global scale. This lab accurately simulates that edge-to-origin relationship.

## 6. Operational Considerations
- **Layered Security:** This lab demonstrates why security cannot rely solely on the backend application. Infrastructure configuration (Nginx) is equally critical.
- **Header Trust:** Backend applications often blindly trust headers (like `X-Forwarded-For` or `Host`) added by proxies. If the proxy doesn't validate these headers, the backend is exposed.
- **Deployment Realism:** Using Docker Compose allows us to spin up this multi-tier architecture locally, mimicking how these services interact across internal networks in production environments without the overhead of Kubernetes.
