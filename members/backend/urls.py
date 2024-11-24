from django.urls import path

from . import views

app_name = "members"

urlpatterns = [
    path("members", views.MemberListView.as_view(), name="members_list"),
    path("members/add", views.MemberAddView.as_view(), name="members_add"),
    path("members/add/bulk", views.MemberBulkLoadView.as_view(), name="members_bulk"),
    path("members/edit/<int:pk>", views.MemberEditView.as_view(), name="members_edit"),
    path("members/delete/<int:pk>", views.MemberDeleteView.as_view(), name="members_delete"),
]
