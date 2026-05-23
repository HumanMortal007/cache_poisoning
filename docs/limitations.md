# Limitations & Future Work

## Lab Limitations

This project is designed specifically as a 6-hour hackathon deliverable. As such, it contains intentional simplifications:

1.  **Lab-Only Environment:** The exploit and mitigation are demonstrated within a controlled Docker network on localhost. It does not account for complex network topologies, NAT traversal, or internet-routing latency.
2.  **Simplified Cache Logic:** Major CDNs (like Cloudflare, Akamai) have highly sophisticated cache rule engines. Our Nginx configuration represents the most basic, fundamental form of caching to clearly illustrate the vulnerability concept without getting bogged down in proprietary CDN syntax.
3.  **No Real CDN Emulation:** We are using an Nginx reverse proxy to *simulate* a CDN edge node. Real CDNs have globally distributed points of presence (PoPs) which introduce issues like cache synchronization and geographic-specific poisoning.
4.  **Limited Browser Simulation:** The automated testing simulates victim requests using the Python `requests` library. While effective for validating the HTTP response, it does not fully execute the JavaScript payload as a real browser (like Chrome or Firefox) would.

## Future Work

If this project were to be expanded into a larger security engineering effort or an extended hackathon, the following enhancements would be prioritized:

1.  **Web Application Firewall (WAF) Integration:** Implement ModSecurity or an equivalent WAF layer in front of the Nginx cache to detect anomalous `Host` headers based on known malicious signatures or behavioral profiling before they even reach the caching logic.
2.  **Distributed Cache Testing:** Expand the Docker Compose architecture to include multiple Nginx edge nodes and test how poisoned cache entries propagate (or fail to propagate) across a distributed network.
3.  **Real Browser Exploitation:** Integrate a headless browser framework (like Selenium or Playwright) into the exploit/validation script to demonstrably execute the injected JavaScript payload and capture screenshots of the defaced application.
4.  **Advanced Payload Delivery:** Currently, the exploit demonstrates reflecting the host to change a script source. Future iterations could explore poisoning redirects (HTTP 301/302) or exploiting unkeyed query parameters alongside the host header.
5.  **Telemetry and Alerting (SIEM):** Implement an ELK stack (Elasticsearch, Logstash, Kibana) or Prometheus/Grafana to ingest Nginx access logs and create real-time alerts when cache hit rates spike for unusual hostnames, indicating a potential ongoing cache poisoning attack.
