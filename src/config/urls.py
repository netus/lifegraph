from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import logout as auth_logout
from django.http import JsonResponse
from django.urls import include, path


def _admin_logout(request):
    """Allow GET/POST logout for admin (Django 5+ requires POST by default)."""
    from django.shortcuts import redirect
    auth_logout(request)
    return redirect(f"/{settings.ADMIN_URL}/")

admin.site.site_header = "LifeGraph"
admin.site.site_title = "LifeGraph"
admin.site.index_title = "管理控制台"

_orig_admin_login = admin.site.login


def _admin_login_with_turnstile(request, extra_context=None):
    return _orig_admin_login(request, extra_context=extra_context)


admin.site.login = _admin_login_with_turnstile

def _resolve_admin_url():
    return settings.ADMIN_URL

_admin_url = _resolve_admin_url()
settings.ADMIN_URL = _admin_url  # 同步给中间件（urls.py 加载早于首次请求）

def healthcheck(request):
    return JsonResponse({"ok": True, "service": "lifegraph"})


urlpatterns = [
    path(f"{_admin_url}/logout/", _admin_logout, name="admin_logout"),
    path(f"{_admin_url}/", admin.site.urls),
    path("healthz", healthcheck, name="healthz"),
    path("", include("apps.lifegraph.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "apps.lifegraph.views.bad_request_handler"
handler403 = "apps.lifegraph.views.permission_denied_handler"
handler404 = "apps.lifegraph.views.not_found_handler"
handler500 = "apps.lifegraph.views.server_error_handler"
