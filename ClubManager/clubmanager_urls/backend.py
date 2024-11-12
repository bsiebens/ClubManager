from django.urls import include, path

from members import views

app_name = "clubmanager_backend"
urlpatterns = [
    path("", views.index, name="index"),
]