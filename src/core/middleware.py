import time
import zoneinfo

from django.conf import settings
from django.contrib import auth, messages
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone

from core.turnstile import verify_turnstile


def get_client_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()[:45]
    return request.META.get("REMOTE_ADDR", "127.0.0.1")[:45]


class TurnstileAdminLoginMiddleware:
    """Verify Cloudflare Turnstile on admin login POST when env config enables it."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.method == "POST"
            and request.path.rstrip("/") == f"/{settings.ADMIN_URL}/login"
            and not settings.DEBUG
            and getattr(settings, "TURNSTILE_ON_ADMIN_LOGIN", False)
            and getattr(settings, "TURNSTILE_ADMIN_SECRET_KEY", "")
        ):
            token = request.POST.get("cf-turnstile-response", "")
            ip = get_client_ip(request)
            if not verify_turnstile(token, settings.TURNSTILE_ADMIN_SECRET_KEY, ip):
                messages.error(request, "人机验证未通过，请重试。")
                return redirect(f"/{settings.ADMIN_URL}/login/")

        return self.get_response(request)


SESSION_LAST_ACTIVITY_KEY = "_last_activity"


class SessionTimeoutMiddleware:
    """Log staff users out after optional admin inactivity timeout."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and request.path.startswith(f"/{settings.ADMIN_URL}/")
            and request.path.rstrip("/") != f"/{settings.ADMIN_URL}/login"
        ):
            timeout_minutes = int(getattr(settings, "ADMIN_SESSION_TIMEOUT_MINUTES", 0) or 0)
            timeout = timeout_minutes * 60
            now = time.time()
            last = request.session.get(SESSION_LAST_ACTIVITY_KEY)

            if timeout and last and (now - last) > timeout:
                auth.logout(request)
                messages.warning(request, "会话已超时，请重新登录。")
                return redirect(f"/{settings.ADMIN_URL}/login/")

            request.session[SESSION_LAST_ACTIVITY_KEY] = now

        return self.get_response(request)


class RateLimitMiddleware:
    """Small cache-backed rate limit for admin login and future API endpoints."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_client_ip(request)
        path = request.path

        if request.method == "POST" and path.rstrip("/") == f"/{settings.ADMIN_URL}/login":
            limit = int(getattr(settings, "RATE_LIMIT_ADMIN_LOGIN", 5) or 0)
            if self._is_rate_limited(ip, "admin_login", limit, 60):
                return HttpResponse("请求过于频繁，请稍后再试。", status=429)

        if path.startswith("/api/"):
            limit = int(getattr(settings, "RATE_LIMIT_API", 60) or 0)
            if self._is_rate_limited(ip, "api", limit, 60):
                return HttpResponse("API 请求过于频繁，请稍后再试。", status=429)

        return self.get_response(request)

    @staticmethod
    def _is_rate_limited(ip, action, limit, window):
        if limit <= 0:
            return False
        cache_key = f"ratelimit:{action}:{ip}"
        cache.get_or_set(cache_key, 0, window)
        try:
            current = cache.incr(cache_key)
        except ValueError:
            cache.set(cache_key, 1, window)
            current = 1
        return current > limit


class TimezoneMiddleware:
    """Activate browser timezone from cookie for admin and template dates."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_name = request.COOKIES.get("browser_tz")
        if tz_name:
            try:
                timezone.activate(zoneinfo.ZoneInfo(tz_name))
            except (zoneinfo.ZoneInfoNotFoundError, KeyError):
                timezone.deactivate()
        else:
            timezone.deactivate()
        return self.get_response(request)


class AdminNoCacheMiddleware:
    """Prevent admin pages from being cached while allowing anonymous HTML caching."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(f"/{settings.ADMIN_URL}/"):
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
            response["Pragma"] = "no-cache"
            response["CDN-Cache-Control"] = "no-store"
        elif (
            not getattr(request, "user", None)
            or not request.user.is_authenticated
        ):
            content_type = response.get("Content-Type", "")
            if "text/html" in content_type and "Cache-Control" not in response:
                response["Cache-Control"] = "public, max-age=120, s-maxage=300"
        return response


class SecurityHeadersMiddleware:
    """Add conservative security headers to public pages."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Permitted-Cross-Domain-Policies"] = "none"
        response["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )

        if request.path.startswith(f"/{settings.ADMIN_URL}/"):
            return response

        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type:
            return response

        response["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' https://static.cloudflareinsights.com; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        return response
