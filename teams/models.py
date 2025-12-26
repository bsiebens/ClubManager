import datetime

from constance import config
from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from rules import is_superuser
from rules.contrib.models import RulesModel

from .rules import is_team_admin


def create_default_season(day: int | None = None, month: int | None = None, duration: str | None = None) -> tuple[datetime.date, datetime.date]:
    """Creates a default season based on the current date."""

    day = config.CM_DEFAULT_SEASON_DAY if day is None else day
    month = config.CM_DEFAULT_SEASON_MONTH if month is None else month
    duration = config.CM_DEFAULT_SEASON_DURATION if duration is None else duration

    current_date = timezone.now()

    # Determine the start year based on the current date
    start_year = current_date.year
    if current_date.month < month or (current_date.month == month and current_date.day < day):
        start_year -= 1

    # Create the start date
    start_date = datetime.date(year=start_year, month=month, day=day)

    # Calculate the end date based on the range string
    range_value = int(duration[:-1])
    range_unit = duration[-1]

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
    return f"teams/picture/{instance.team.slug}/{instance.season.start_date.year}/{filename}"


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
            models.CheckConstraint(condition=models.Q(start_date__lt=models.F("end_date")), name="season_start_date_lt_end_date", violation_error_message=_("Start date must be before end date.")),
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


class TeamRole(RulesModel):
    """
    Represents a team role within a system, defining various attributes and
    permissions associated with the role.

    :ivar name: The name of the role.
    :type name: str
    :ivar abbreviation: An abbreviated version of the role name.
    :type abbreviation: str
    :ivar staff_role: Indicates whether the role is a supporting function
        for a team, such as a coach or manager.
    :type staff_role: bool
    :ivar admin_role: Indicates whether the role has administrative privileges
        to manage team information and settings.
    :type admin_role: bool
    :ivar sort_order: Defines the display order of the role (sorted from low to high).
    :type sort_order: int
    """

    name = models.CharField(_("name"), max_length=255, unique=True)
    abbreviation = models.CharField(_("abbreviation"), max_length=255, unique=True, help_text=_("An abbreviated version of the role name"))

    staff_role = models.BooleanField(_("staff role"), default=False, help_text=_("A staff role is any supporting function for a given team (e.g., coach, team manager, ...)"))
    admin_role = models.BooleanField(_("admin role"), default=False, help_text=_("An admin role is a role that has administrative privileges and can change team information and settings"))

    sort_order = models.PositiveIntegerField(_("sort order"), default=10, help_text=_("The order in which the role should be displayed (low to high)"))

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("team role")
        verbose_name_plural = _("team roles")
        ordering = ["sort_order", "name"]
        rules_permissions = {"add": is_superuser, "view": is_superuser, "change": is_superuser, "delete": is_superuser}

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class Team(RulesModel):
    """
    Represents a Team, providing information about its name, type, members, and other attributes.

    :ivar name: Full name of the team. Must be unique and is a required field.
    :type name: str
    :ivar short_name: Optional short name for the team. Can be left blank or null.
    :type short_name: str
    :ivar slug: Unique and automatically generated slug value based on the team's
        name. Used for SEO or URL-friendly paths.
    :type slug: str
    :ivar type: Type of team, representing whether it is internal or external. Defaults
        to "Internal".
    :type type: str
    :ivar logo: Optional logo image for the team, stored in the path "teams/logo/".
    :type logo: ImageField
    :ivar members: Related members associated with the team, defined with
        many-to-many relationships through the "TeamMembership" model.
    :type members: ManyToManyField
    """

    class TeamTypes(models.TextChoices):
        INTERNAL = "INT", _("Internal")
        EXTERNAL = "EXT", _("External")

    name = models.CharField(_("name"), max_length=255, unique=True)
    short_name = models.CharField(_("short name"), max_length=255, unique=True, blank=True, null=True, help_text=_("An optional short name for the team"))
    slug = AutoSlugField(_("slug"), max_length=255, unique=True, populate_from="name")
    type = models.CharField(_("type"), max_length=3, choices=TeamTypes.choices, default=TeamTypes.INTERNAL)
    logo = models.ImageField(_("logo"), upload_to="teams/logo/", blank=True, null=True)

    members = models.ManyToManyField("members.Member", verbose_name=_("members"), through="TeamMembership")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("team")
        verbose_name_plural = _("teams")
        ordering = ["name"]
        rules_permissions = {"add": is_superuser, "view": is_superuser, "change": is_superuser, "delete": is_superuser}

    def __str__(self):
        return self.short_name

    @property
    def initials(self) -> str:
        words = self.name.split()
        if len(words) == 1:
            return words[0][0].upper()

        return "".join(word[0].upper() for word in words[:2])

    @property
    def member_count(self) -> int:
        season = Season.for_date()
        return self.members.filter(team_memberships__season=season).count()

    def get_short_name(self) -> str:
        """Returns the short name of the team, or the name if no short name is set."""
        return self.short_name if self.short_name and self.short_name != "" else self.name


class TeamMembership(RulesModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name=_("team"))
    member = models.ForeignKey("members.Member", on_delete=models.CASCADE, related_name="team_memberships", verbose_name=_("member"))
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="team_memberships", verbose_name=_("season"))
    role = models.ForeignKey(TeamRole, on_delete=models.CASCADE, related_name="team_memberships", verbose_name=_("role"))

    number = models.PositiveIntegerField(_("number"), blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(99)])
    captain = models.BooleanField(_("captain"), default=False)
    alternate_captain = models.BooleanField(_("alternate captain"), default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("team membership")
        verbose_name_plural = _("team memberships")
        ordering = ["team__name", "role__sort_order", "number", "member__user__last_name", "member__user__first_name"]
        constraints = [
            models.UniqueConstraint(fields=["team", "season", "number"], name="unique_team_membership_number", violation_error_message=_("A team can only have one member for a given season and number.")),
        ]
        rules_permissions = {"add": is_superuser | is_team_admin, "view": is_superuser | is_team_admin, "change": is_superuser | is_team_admin, "delete": is_superuser | is_team_admin}

    def __str__(self):
        return f"{self.team.name} - {self.member.user.get_full_name()} ({self.role.abbreviation})"


class TeamPicture(RulesModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name=_("team"))
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name=_("season"))
    picture = models.ImageField(_("picture"), upload_to=team_season_file_path)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("team picture")
        verbose_name_plural = _("team pictures")
        ordering = ["team__name", "season__start_date"]
        rules_permissions = {"add": is_superuser, "view": is_superuser, "change": is_superuser, "delete": is_superuser}

    def __str__(self):
        return f"{self.team.name} - {self.season.start_date.year}"
