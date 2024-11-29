#  Copyright (c) ClubManager - Bernard Siebens 2024.
from dateutil.relativedelta import relativedelta
from django import forms
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from .models import Season


class SeasonCreationForm(forms.Form):
    class DurationChoices(TextChoices):
        DAY = "d", _("day(s)")
        WEEK = "w", _("week(s)")
        MONTH = "m", _("month(s)")
        QUARTER = "q", _("quarter(s)")
        YEAR = "y", _("year(s)")

    duration = forms.IntegerField(label=_("duration"), initial=1)
    unit = forms.ChoiceField(label=_("unit"), choices=DurationChoices.choices, initial=DurationChoices.YEAR)

    def save_season(self) -> Season:
        last_season = Season.objects.order_by("-end_date").first()

        start_date = last_season.end_date + relativedelta(days=+1)
        end_date = start_date + relativedelta(days=-1)

        match self.cleaned_data["unit"]:
            case self.DurationChoices.DAY:
                end_date = end_date + relativedelta(days=self.cleaned_data["duration"])
            case self.DurationChoices.WEEK:
                end_date = end_date + relativedelta(weeks=self.cleaned_data["duration"])
            case self.DurationChoices.MONTH:
                end_date = end_date + relativedelta(months=self.cleaned_data["duration"])
            case self.DurationChoices.QUARTER:
                end_date = end_date + relativedelta(months=+self.cleaned_data["duration"] * 3)
            case self.DurationChoices.YEAR:
                end_date = end_date + relativedelta(years=self.cleaned_data["duration"])

        new_season = Season.objects.create(start_date=start_date, end_date=end_date)
        return new_season
