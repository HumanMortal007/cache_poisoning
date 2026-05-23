# Threat Model: Web Cache Poisoning via Host Header Injection

## 1. System Overview
The target system is a cloud-native web application architecture consisting of an Nginx reverse proxy acting as a caching edge layer, and a Python Flask backend application. 

## 2. Attacker Profile
- **Type:** External unauthenticated attacker.
- **Capability:** Low to Medium. Requires understanding of HTTP headers and caching mechanics, but no specialized zero-day exploits.
- **Motivation:** Defacement, Cross-Site Scripting (XSS), malware distribution, or denial of service.

## 3. Attack Surface
The primary attack surface is the HTTP request processing pipeline, specifically:
- The Nginx caching configuration (`proxy_cache_key`).
- The Flask application's handling of the HTTP `Host` header.

## 4. Trust Boundaries
- **External to Nginx:** Untrusted. All incoming HTTP requests.
- **Nginx to Flask:** Partially Trusted. Nginx is expected to sanitize or validate requests, but currently forwards the `Host` header unmodified.
- **Flask Application:** Trusted internally, but currently misplaces trust in the unvalidated `Host` header provided by the proxy.

## 5. Assets at Risk
- **Integrity of Cached Content:** The primary asset.
- **User Client Security:** Users interacting with poisoned content may execute malicious scripts.
- **Brand Reputation:** Serving malicious content damages trust.

## 6. Threat Scenario (STRIDE)
- **Spoofing:** The attacker spoofs the intended destination by injecting a malicious `Host` header.
- **Tampering:** The attacker tampers with the application's response by forcing it to include the malicious host in dynamically generated URLs.
- **Information Disclosure:** (Secondary) Potential exposure of internal application logic if verbose errors are triggered.
- **Denial of Service:** (Secondary) The attacker could poison the cache with a host that points to a non-existent server, effectively breaking the application for legitimate users.

## 7. Vulnerability Analysis
The vulnerability exists due to a mismatch between what the cache considers "unique" and what the application considers "input".
1. **Cache Key:** Nginx uses only `$uri` (the path). It assumes all requests to `/` should receive the same cached response.
2. **Application Logic:** Flask uses the `Host` header to generate absolute URLs within the response body.
3. **Exploitation:** By sending a request to `/` with `Host: evil.com`, the cache stores the response containing `evil.com` under the key `/`. Subsequent legitimate requests to `/` receive the poisoned response.

## 8. Mitigation Strategy
The mitigation must address the root cause at the infrastructure layer:
1. **Cache Key Normalization:** Include the `Host` header in the cache key (`proxy_cache_key $http_host$uri;`). This ensures responses generated for different hosts are cached separately.
2. **Header Validation:** Explicitly define allowed `server_name` directives in Nginx and use the validated `$host` variable instead of the raw `$http_host` when proxying to the backend.
3. **Default Drop:** Configure a default server block in Nginx to drop requests (e.g., return 444) that do not match known, valid hostnames.
