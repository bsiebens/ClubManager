#  Copyright (c) ClubManager - Bernard Siebens 2024.
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, FormView, DeleteView
from rules.contrib.views import PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _

from ..forms import SeasonCreationForm
from ..models import Season


class SeasonListView(PermissionRequiredMixin, ListView):
    model = Season
    permission_required = 'teams.view_season'
    permission_denied_message = _("You do not have permission to view this page")

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["form"] = SeasonCreationForm()

        return context

class SeasonAddView(PermissionRequiredMixin, SuccessMessageMixin, FormView):
    permission_required = 'teams.add_season'
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
    permission_required = 'teams.delete_season'
    permission_denied_message = _("You do not have permission to view this page")
    success_url = reverse_lazy("backend:teams:seasons_list")
    success_message = _("Season has been deleted successfully")

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))