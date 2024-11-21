from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django_filters.views import FilterView

from members.models import Member


class MemberListView(FilterView, LoginRequiredMixin, UserPassesTestMixin):
    model = Member
    login_url = reverse_lazy("two_factor:login")
    permission_denied_message = _("You do not have permission to view this page.")

    def test_func(self) -> bool:
        return self.request.user.is_superuser

    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, self.get_permission_denied_message())
        return HttpResponseRedirect(reverse_lazy("two_factor:login"))