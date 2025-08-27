from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Referrer-Policy
        response.setdefault("Referrer-Policy", getattr(settings, "REFERRER_POLICY", "same-origin"))
        # Permissions-Policy (formerly Feature-Policy)
        response.setdefault("Permissions-Policy", getattr(settings, "PERMISSIONS_POLICY", "geolocation=(), camera=(), microphone=()"))
        # Cross-Origin-Opener-Policy
        response.setdefault("Cross-Origin-Opener-Policy", getattr(settings, "COOP", "same-origin"))
        # Cross-Origin-Resource-Policy
        response.setdefault("Cross-Origin-Resource-Policy", getattr(settings, "CORP", "same-origin"))
        # Content-Security-Policy (tight for API-only)
        csp = getattr(settings, "CONTENT_SECURITY_POLICY", "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'; connect-src 'self'")
        if csp:
            response.setdefault("Content-Security-Policy", csp)
        return response

