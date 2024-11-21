"""
URL configuration for ClubManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView
from two_factor.urls import urlpatterns as two_factor_urls

urlpatterns = [
    path("", include(two_factor_urls)),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/profile/", RedirectView.as_view(pattern_name="clubmanager:index"), name="profile"),
    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path("accounts/password_change/done/", auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("clubmanager/backend/", include("ClubManager.clubmanager_urls.backend")),
    path("clubmanager/", include("ClubManager.clubmanager_urls.frontend")),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + [
        path('admin/', admin.site.urls),
    ]