import csv
import io

from constance import config
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, FormView, UpdateView
from django_filters.views import FilterView
from rules.contrib.views import PermissionRequiredMixin

from ..filters import MemberFilter
from ..forms import MassUploadForm, MemberForm
from ..models import Member


class MemberListView(PermissionRequiredMixin, FilterView):
    filterset_class = MemberFilter
    paginate_by = 50
    permission_denied_message = _("You do not have permission to view this page.")
    permission_required = "members.view_member"

    def test_func(self) -> bool:
        return self.request.user.is_superuser

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))


class MemberAddView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Member
    form_class = MemberForm
    success_url = reverse_lazy("backend:members:members_list")
    success_message = _("Member <strong>%(name)s</strong> has been added successfully - <strong>%(note)s</strong>")
    permission_denied_message = _("You do not have permission to view this page.")
    permission_required = "members.add_member"

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % dict(cleaned_data, name=self.object.user.get_full_name(), note=self.object.notes)

    def test_func(self) -> bool:
        return self.request.user.is_superuser

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))


class MemberEditView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Member
    form_class = MemberForm
    success_url = reverse_lazy("backend:members:members_list")
    success_message = _("Member <strong>%(name)s</strong> has been edited successfully - <strong>%(note)s</strong>")
    permission_denied_message = _("You do not have permission to view this page.")
    permission_required = "members.change_member"

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % dict(cleaned_data, name=self.object.user.get_full_name(), note=self.object.notes)

    def test_func(self) -> bool:
        return self.request.user.is_superuser

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def get_initial(self) -> dict[str, str]:
        initial_data = super().get_initial()

        initial_data["first_name"] = self.object.user.first_name
        initial_data["last_name"] = self.object.user.last_name
        initial_data["email"] = self.object.user.email
        initial_data["admin"] = self.object.user.is_superuser

        return initial_data


class MemberDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Member
    success_url = reverse_lazy("backend:members:members_list")
    success_message = _("Member <strong>%(name)s</strong> has been deleted successfully")
    permission_denied_message = _("You do not have permission to view this page.")
    permission_required = "members.delete_member"

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % dict(cleaned_data, name=self.object.user.get_full_name(), note=self.object.notes)

    def test_func(self) -> bool:
        return self.request.user.is_superuser

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))


class MemberBulkLoadView(PermissionRequiredMixin, SuccessMessageMixin, FormView):
    success_url = reverse_lazy("backend:members:members_list")
    success_message = _("Members have been uploaded successfully")
    permission_denied_message = _("You do not have permission to view this page.")
    template_name = "members/member_bulk_upload.html"
    form_class = MassUploadForm
    permission_required = "members.add_member"

    def test_func(self) -> bool:
        return self.request.user.is_superuser

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("backend:index"))

    def form_valid(self, form: MassUploadForm) -> HttpResponse:
        member_data = self.request.FILES["data_file"]

        with io.TextIOWrapper(member_data.file) as csvfile:
            reader = csv.reader(csvfile)

            for row in reader:
                first_name = row[0]
                last_name = row[1]
                email = row[2]
                birthday = row[3]
                license_number = row[4]

                member = Member.create_member(first_name=first_name, last_name=last_name, email=email)

                if birthday is not None and birthday != "":
                    member.birthday = birthday

                if license_number is not None and license_number != "":
                    member.license = license_number

                member.save(update_fields=["birthday", "license"])

                if config.CLUBMANAGER_ENABLE_TEAMS:
                    # TODO (Bernard Siebens): Should process any team related information here and store the necessary links to teams
                    raise NotImplementedError("Teams module is not yet implemented")

        return super().form_valid(form)
