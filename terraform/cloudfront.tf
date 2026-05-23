# -----------------------------------------------------------------------------
# AWS CloudFront Distribution (Edge Cache Proxy)
# Demonstrating the mitigation for Host Header Injection in a Cloud-Native architecture
# -----------------------------------------------------------------------------

resource "aws_cloudfront_distribution" "cdn_proxy" {
  enabled = true

  origin {
    domain_name = aws_lb.flask_backend.dns_name
    origin_id   = "flask-backend-origin"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "flask-backend-origin"

    # =========================================================================
    # MITIGATION FOR HOST HEADER CACHE POISONING
    # =========================================================================
    # By default, CloudFront forwards the original Host header to the origin
    # but does NOT include it in the Cache Key. This is the exact vulnerability 
    # demonstrated in our Nginx lab.
    # 
    # The fix is to attach a Cache Policy that explicitly includes the 'Host' 
    # header in the cache key.
    cache_policy_id = aws_cloudfront_cache_policy.secure_cache_policy.id

    viewer_protocol_policy = "redirect-to-https"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# -----------------------------------------------------------------------------
# Secure Cache Policy (The Fix)
# -----------------------------------------------------------------------------
resource "aws_cloudfront_cache_policy" "secure_cache_policy" {
  name        = "Secure-Cache-Policy-Host-Header"
  description = "A secure cache policy that includes the Host header in the Cache Key to prevent cache poisoning."

  # Default TTL settings
  default_ttl = 600
  max_ttl     = 3600
  min_ttl     = 0

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    headers_config {
      header_behavior = "whitelist"
      headers {
        # MITIGATION: Include the Host header in the Cache Key
        items = ["Host"]
      }
    }
    query_strings_config {
      query_string_behavior = "none"
    }
  }
}
