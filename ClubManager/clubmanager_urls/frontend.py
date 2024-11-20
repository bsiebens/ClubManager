from django.urls import include, path
from django.views.generic import RedirectView

app_name = "clubmanager_frontend"
urlpatterns = [
    path("", RedirectView.as_view(pattern_name="clubmanager_configuration"), name="index"),
]