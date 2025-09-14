import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rules import is_superuser
from rules.contrib.models import RulesModel


def create_default_season() -> tuple[datetime.date, datetime.date]:
    """Creates a default season based on the current date."""

    current_date = timezone.now()

    # Determine the start year based on the current date
    start_year = current_date.year
    if current_date.month < settings.CM_DEFAULT_SEASON_MONTH or (current_date.month == settings.CM_DEFAULT_SEASON_MONTH and current_date.day < settings.CM_DEFAULT_SEASON_DAY):
        start_year -= 1

    # Create the start date
    start_date = datetime.date(year=start_year, month=settings.CM_DEFAULT_SEASON_MONTH, day=settings.CM_DEFAULT_SEASON_DAY)

    # Calculate the end date based on the range string
    range_value = int(settings.CM_DEFAULT_SEASON_DURATION[:-1])
    range_unit = settings.CM_DEFAULT_SEASON_DURATION[-1]

    end_date = start_date
    match range_unit:
        case "y":
            end_date += relativedelta(years=range_value)
        case "m":
            end_date += relativedelta(months=range_value)
        case "d":
            end_date += relativedelta(days=range_value)
        case "w":
            end_date += relativedelta(weeks=range_value)
        case _:
            raise ValueError(f"Invalid range unit: {range_unit}, supported units are: y, m, d, w")

    end_date -= relativedelta(days=1)
    return start_date, end_date


def team_season_file_path(instance: "TeamPicture", filename: str) -> str:
    """Generates the file path for a team picture based on the team name and season."""
    return f"groups/picture/{instance.team.slug}/{instance.season.start_date.year}/{filename}"


class Season(RulesModel):
    """
    Represents a seasonal period within a certain time frame.

    :ivar start_date: The start date of the season.
    :type start_date: datetime.date
    :ivar end_date: The end date of the season.
    :type end_date: datetime.date
    """

    start_date = models.DateField(_("start_date"))
    end_date = models.DateField(_("end_date"))

    class Meta:
        verbose_name = _("season")
        verbose_name_plural = _("seasons")
        ordering = ["start_date"]
        rules_permissions = {"add": is_superuser, "view": is_superuser, "change": is_superuser, "delete": is_superuser}
        constraints = [
            models.UniqueConstraint(fields=["start_date", "end_date"], name="season_start_date_end_date_unique", violation_error_message=_("Start and end date for a given season must be unique.")),
            models.CheckConstraint(check=models.Q(start_date__lt=models.F("end_date")), name="season_start_date_lt_end_date", violation_error_message=_("Start date must be before end date.")),
        ]

    def __str__(self):
        return _("Season '{start_date} - '{end_date}").format(start_date=self.start_date.strftime("%y"), end_date=self.end_date.strftime("%y"))

    @property
    def date_range(self) -> tuple[datetime.date, datetime.date]:
        return self.start_date, self.end_date

    @property
    def is_current(self) -> bool:
        return self.start_date <= timezone.now().date() <= self.end_date

    @classmethod
    def for_date(cls, current_date: datetime.date | None = None, values_only: bool = False) -> "tuple[datetime.date, datetime.date] | Season":
        """Returns the season object based on the provided date (if `current_date` is None will default to the current date)."""

        if current_date is None:
            current_date = timezone.now().date()

        season = cls.objects.get(start_date__lte=current_date, end_date__gte=current_date)

        return season.date_range if values_only else season
