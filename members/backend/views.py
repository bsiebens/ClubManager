from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django_filters.views import FilterView
from django.utils.translation import gettext_lazy as _

from ..filters import MemberFilter
from ..models import Member
from ..forms import MemberForm

class MemberListView(LoginRequiredMixin, UserPassesTestMixin, FilterView):
    filterset_class = MemberFilter
    paginate_by = 50
    login_url = reverse_lazy("two_factor:login")
    permission_denied_message = _("You do not have permission to view this page.")

    def test_func(self) -> bool:
        return self.request.user.is_superuser

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("two_factor:login"))

class MemberAddView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Member
    form_class = MemberForm
    success_url = reverse_lazy("backend:members:members_list")
    success_message = _("Member <strong>%(name)s</strong> has been added successfully - <strong>%(note)s</strong>")
    login_url = reverse_lazy("two_factor:login")
    permission_denied_message = _("You do not have permission to view this page.")

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % dict(cleaned_data, name=self.object.user.get_full_name(), note=self.object.notes)

    def test_func(self) -> bool:
        return self.request.user.is_superuser

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("two_factor:login"))

class MemberEditView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Member
    form_class = MemberForm
    success_url = reverse_lazy("backend:members:members_list")
    success_message = _("Member <strong>%(name)s</strong> has been edited successfully - <strong>%(note)s</strong>")
    permission_denied_message = _("You do not have permission to view this page.")
    login_url = reverse_lazy("two_factor:login")

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % dict(cleaned_data, name=self.object.user.get_full_name(), note=self.object.notes)

    def test_func(self) -> bool:
        return self.request.user.is_superuser

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("two_factor:login"))

    def get_initial(self) -> dict[str, str]:
        initial_data = super().get_initial()

        initial_data["first_name"] = self.object.user.first_name
        initial_data["last_name"] = self.object.user.last_name
        initial_data["email"] = self.object.user.email
        initial_data["admin"] = self.object.user.is_superuser

        return initial_data