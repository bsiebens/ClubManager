"""
URL configuration for the ClubManager project.

The `urlpatterns` list routes URLs to views. For more information, please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="clubmanager:news"), name="home"),
    path("clubmanager/", include("ClubManager.frontend.urls")),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    # path("api/", include(router.urls)),
    # path("api-auth/", include("rest_framework.urls")),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + debug_toolbar_urls()

js_info_dict = {
    "packages": ("recurrence",),
}

urlpatterns = urlpatterns + [path("jsi18n/", JavaScriptCatalog.as_view(packages=["recurrence"]), name="javascript-catalog")]
