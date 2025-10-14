from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="clubmanager:news"), name="home"),
    path("clubmanager/", include("ClubManager.frontend.urls")),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("markdownx/", include("markdownx.urls")),
    path("webpush/", include("webpush.urls")),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += (
        [
            path("__reload__/", include("django_browser_reload.urls")),
        ]
        + debug_toolbar_urls()
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )

js_info_dict = {
    "packages": ("recurrence",),
}

urlpatterns = urlpatterns + [path("jsi18n/", JavaScriptCatalog.as_view(packages=["recurrence"]), name="javascript-catalog")]
