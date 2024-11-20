import django_filters
from django.utils.translation import gettext_lazy as _

from .models import Member


class MemberFilter(django_filters.FilterSet):
    user__first_name = django_filters.CharFilter(label=_("First Name"), lookup_expr="icontains")
    user__last_name = django_filters.CharFilter(label=_("Last Name"), lookup_expr="icontains")

    class Meta:
        model = Member
        fields = ["user__first_name", "user__last_name"]
