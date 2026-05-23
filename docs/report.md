# Formal Report: Web Cache Poisoning via Host Header Injection

## Abstract
This report details the implementation, exploitation, and mitigation of a Web Cache Poisoning vulnerability utilizing Host Header Injection within a cloud-native architecture. The project simulates a realistic edge-caching scenario using Nginx and a Python Flask backend. We demonstrate how a misalignment between infrastructure caching keys and backend application logic allows an attacker to compromise the infrastructure (MITRE ATT&CK T1584), serving malicious payloads to legitimate users. We further provide and validate configuration-based mitigations to secure the environment.

## 1. Introduction
Modern web architectures heavily utilize Content Delivery Networks (CDNs) and reverse proxies to optimize performance. These systems cache responses to reduce backend load. However, complex HTTP header handling can introduce subtle vulnerabilities. Web Cache Poisoning occurs when an attacker manipulates a request such that the application generates a harmful response, which the cache then stores and serves to other users. This project specifically examines the abuse of the HTTP `Host` header.

## 2. Objectives
- Design a realistic, lightweight, containerized environment demonstrating the vulnerability.
- Develop an automated exploitation tool to prove the concept.
- Implement infrastructural mitigations to remediate the vulnerability.
- Validate the effectiveness of the mitigations through automated testing.
- Align the attack methodology with industry standards (MITRE ATT&CK).

## 3. Architecture
The architecture follows a standard two-tier cloud-native model deployed via Docker Compose:
- **Edge Layer (Nginx):** Configured as a reverse proxy with `proxy_cache` enabled. This simulates a CDN edge node.
- **Backend Application (Flask):** A Python-based application that dynamically renders HTML content, simulating a modern web application that relies on the `Host` header for internal routing or resource loading.

## 4. Implementation
The vulnerability is rooted in a specific misconfiguration:
- **Nginx (Vulnerable):** Defines the cache key solely based on the request URI (`proxy_cache_key $uri;`). It forwards the client's `Host` header unmodified to the backend (`proxy_set_header Host $http_host;`).
- **Flask (Backend):** Reads the incoming `Host` header and reflects it within an HTML `<script>` tag attribute.

## 5. Attack Methodology
1. **Target Identification:** The attacker identifies that the target caches responses and that the backend application reflects the `Host` header.
2. **Injection:** The attacker sends a request to the target URI (e.g., `/`) while injecting a malicious `Host` header (e.g., `Host: attacker.com`).
3. **Poisoning:** Nginx forwards the request. Flask generates a response containing `<script src="http://attacker.com/...">`. Nginx caches this response under the key `/`.
4. **Execution:** A legitimate user requests `/` with a normal `Host` header. Nginx serves the cached, poisoned response. The user's browser executes the script from `attacker.com`.

## 6. Mitigation
Remediation must occur at the infrastructure layer, as the cache is the component serving the malicious content to unintended victims.
1. **Cache Key Normalization:** The cache key must include the `Host` header. Nginx is updated to use `proxy_cache_key $http_host$uri;`. This ensures that a request with `Host: attacker.com` does not overwrite the cache for `Host: legitimate.com`.
2. **Strict Host Validation:** Nginx is configured with explicit `server_name` directives. The proxy configuration uses the validated `$host` variable (`proxy_set_header Host $host;`) instead of the unvalidated `$http_host`.
3. **Default Drop:** A default server block is implemented to drop requests (HTTP 444) that do not match the defined `server_name`, preventing the backend from ever processing malicious hosts.

## 7. Results
The provided validation script (`tests/validate.py`) confirms:
- **Pre-mitigation:** The exploit script successfully poisons the cache, and a subsequent simulated victim request receives the attacker's payload.
- **Post-mitigation:** The exploit script fails to affect the cache for legitimate users. Requests with invalid hosts are either isolated in the cache or rejected outright.

## 8. Conclusion
Web Cache Poisoning is a critical vulnerability that turns an organization's performance infrastructure into an attack vector. This project demonstrates that relying solely on application-level security is insufficient in cloud-native deployments. Robust infrastructural configuration, specifically regarding cache key normalization and strict header validation, is essential for defense in depth.

## 9. References
- PortSwigger: Web Cache Poisoning (https://portswigger.net/web-security/web-cache-poisoning)
- MITRE ATT&CK: T1584 - Compromise Infrastructure (https://attack.mitre.org/techniques/T1584/)
- Nginx Documentation: proxy_cache_key (https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache_key)
