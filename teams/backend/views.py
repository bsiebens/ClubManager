#  Copyright (c) ClubManager - Bernard Siebens 2024.
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, FormView, ListView, UpdateView
from django_filters.views import FilterView
from rules.contrib.views import PermissionRequiredMixin

from ..filters import TeamRoleFilter
from ..forms import SeasonCreationForm, NumberPoolCreationForm
from ..models import Season, TeamRole, NumberPool


class SeasonListView(PermissionRequiredMixin, ListView):
    model = Season
    permission_required = "teams.view_season"
    permission_denied_message = _("You do not have permission to view this page")

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["form"] = SeasonCreationForm()

        return context


class SeasonAddView(PermissionRequiredMixin, SuccessMessageMixin, FormView):
    permission_required = "teams.add_season"
    permission_denied_message = _("You do not have permission to view this page")
    form_class = SeasonCreationForm
    template_name = "teams/season_form.html"
    success_url = reverse_lazy("backend:teams:seasons_list")
    success_message = _("Season has been added successfully")

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def form_valid(self, form: SeasonCreationForm) -> HttpResponse:
        form.save_season()
        return super().form_valid(form)


class SeasonDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Season
    permission_required = "teams.delete_season"
    permission_denied_message = _("You do not have permission to view this page")
    success_url = reverse_lazy("backend:teams:seasons_list")
    success_message = _("Season has been deleted successfully")

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def form_valid(self, form) -> HttpResponse:
        if self.object.passed_start_date:
            messages.error(self.request, _("You cannot delete a passed season or one that is already started"))
            return HttpResponseRedirect(reverse_lazy("backend:teams:seasons_list"))

        return super().form_valid(form)


class TeamRoleListView(PermissionRequiredMixin, FilterView):
    filterset_class = TeamRoleFilter
    permission_required = "teams.view_teamrole"
    permission_denied_message = _("You do not have permission to view this page")
    paginate_by = 50

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))


class TeamRoleAddView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = TeamRole
    fields = ["name", "abbreviation", "staff_role", "admin_role", "sort_order"]
    permission_required = "teams.add_teamrole"
    permission_denied_message = _("You do not have permission to view this page")
    success_url = reverse_lazy("backend:teams:teamroles_list")
    success_message = _("Team role <strong>%(name)s (%(abbreviation)s)</strong> has been added successfully")

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % dict(cleaned_data, name=self.object.name, abbreviation=self.object.abbreviation)


class TeamRoleEditView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TeamRole
    fields = ["name", "abbreviation", "staff_role", "admin_role", "sort_order"]
    permission_required = "teams.change_teamrole"
    permission_denied_message = _("You do not have permission to view this page")
    success_url = reverse_lazy("backend:teams:teamroles_list")
    success_message = _("Team role <strong>%(name)s (%(abbreviation)s)</strong> has been edited successfully")

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % dict(cleaned_data, name=self.object.name, abbreviation=self.object.abbreviation)


class TeamRoleDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = TeamRole
    permission_required = "teams.delete_teamrole"
    permission_denied_message = _("You do not have permission to view this page")
    success_url = reverse_lazy("backend:teams:teamroles_list")
    success_message = _("Team role <strong>%(name)s (%(abbreviation)s)</strong> has been deleted successfully")

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % dict(cleaned_data, name=self.object.name, abbreviation=self.object.abbreviation)

class NumberPoolListView(PermissionRequiredMixin, ListView):
    model = NumberPool
    permission_required = "teams.view_numberpool"
    permission_denied_message = _("You do not have permission to view this page")

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["form"] = NumberPoolCreationForm()

        return context


class NumberPoolAddView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = NumberPool
    fields = ["name", "enforce_unique_numbers"]
    permission_required = "teams.add_numberpool"
    permission_denied_message = _("You do not have permission to view this page")
    success_url = reverse_lazy("backend:teams:numberpools_list")
    success_message = _("Number pool <strong>%(name)s</strong> has been added successfully")

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % dict(cleaned_data, name=self.object.name, abbreviation=self.object.name)


class NumberPoolDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = NumberPool
    permission_required = "teams.delete_numberpool"
    permission_denied_message = _("You do not have permission to view this page")
    success_url = reverse_lazy("backend:teams:numberpools_list")
    success_message = _("Number pool <strong>%(name)s</strong> has been deleted successfully")

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % dict(cleaned_data, name=self.object.name, abbreviation=self.object.name)

    def form_valid(self, form) -> HttpResponse:
        if self.object.name == "default":
            messages.error(self.request, _("You cannot delete the default number pool"))
            return HttpResponseRedirect(reverse_lazy("backend:teams:numberpools_list"))

        return super().form_valid(form)