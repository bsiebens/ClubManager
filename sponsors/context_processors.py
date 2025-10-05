from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.utils import timezone

from .models import Sponsor


def get_main_sponsors(request: HttpRequest) -> dict[str, QuerySet[Sponsor, Sponsor]]:
    sponsors = Sponsor.objects.filter(main_sponsor=True, start_date__lte=timezone.now()).filter(Q(end_date__gte=timezone.now()) | Q(end_date__isnull=True))
    sponsor_count = sponsors.count()

    return {"sponsors": sponsors, "sponsors_count": sponsor_count}
