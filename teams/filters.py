#  Copyright (c) ClubManager - Bernard Siebens 2024.

import django_filters
from django.utils.translation import gettext_lazy as _

from .models import TeamRole, Team


class TeamRoleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", label=_("name"))

    class Meta:
        model = TeamRole
        fields = ["name"]

class TeamFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", label=_("name"))

    class Meta:
        model = Team
        fields = ["type", "name"]