import datetime
import importlib
from collections import OrderedDict

from constance import config
from django.db import models
from django.db.models import Q, Prefetch, QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel
from recurrence.fields import RecurrenceField
from rules import is_superuser
from rules.contrib.models import RulesModel
from simple_history.models import HistoricalRecords

from members.models import Member
from teams.models import Season, Team
from teams.rules import is_a_team_admin


def grouped_by_response(registrations, buckets=None, order_inside_bucket: bool = True) -> "OrderedDict[str, list[Registration]]":
    """
    Groups registrations into specified buckets based on their response options.

    This method organizes a list of `Registration` objects into groups (buckets)
    defined by their response statuses. By default, it categorizes responses
    into `attending`, `not_attending`, and `no_response` buckets, allowing
    customization via the `buckets` parameter. Additionally, individual
    buckets can be ordered by members' last and first names if desired.

    :param registrations: The list of `Registration` objects to group.
    :param buckets: The mapping of bucket names to corresponding sets of
      response statuses. If not provided, a default set of buckets will be used.
    :param order_inside_bucket: A boolean flag indicating whether to order
      registrations within each bucket by members' last and first names.
    :return: An `OrderedDict` where keys are bucket names and values are lists
      of `Registration` objects corresponding to each bucket.
    """

    if buckets is None:
        buckets = OrderedDict(
            [
                (
                    "attending",
                    {
                        Registration.ResponseOptions.ATTENDING,
                        Registration.ResponseOptions.SELECTED,
                        Registration.ResponseOptions.NOT_SELECTED,
                    },
                ),
                ("not attending", {Registration.ResponseOptions.NOT_ATTENDING}),
                ("no response", {Registration.ResponseOptions.NO_RESPONSE}),
            ]
        )

    response_to_bucket = {status: bucket_name for bucket_name, statuses in buckets.items() for status in statuses}
    grouped = OrderedDict((bucket_name, []) for bucket_name in buckets.keys())

    for registration in registrations:
        bucket_name = response_to_bucket.get(registration.response)
        if bucket_name is not None:
            grouped[bucket_name].append(registration)

    if order_inside_bucket:
        for bucket_list in grouped.values():
            bucket_list.sort(
                key=lambda r: (
                    (getattr(r.member.user, "last_name", "") or "").lower(),
                    (getattr(r.member.user, "first_name", "") or "").lower(),
                )
            )

    return grouped


class Opponent(RulesModel):
    """
    Represents an opponent in a competition or event.

    :ivar name: The name of the opponent, which must be unique.
    :type name: str
    :ivar logo: Optional logo of the opponent, stored as an image file in a
        specific directory.
    :type logo: Optional[ImageField]
    """

    name = models.CharField(_("name"), max_length=255, unique=True)
    logo = models.ImageField(_("logo"), upload_to="opponents/logo/", blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("opponent")
        verbose_name_plural = _("opponents")
        ordering = ["name"]
        rules_permissions = {"add": is_a_team_admin, "view": is_a_team_admin, "change": is_a_team_admin, "delete": is_a_team_admin}

    def __str__(self):
        return self.name

    @property
    def initials(self) -> str:
        words = self.name.split()
        if len(words) == 1:
            return words[0][0].upper()

        return "".join(word[0].upper() for word in words[:2])


class Competition(RulesModel):
    """
    Represents a competition with specific rules and characteristics.

    :ivar name: The name of the competition.
    :type name: models.CharField
    :ivar module: The module associated with the competition.
    :type module: models.CharField
    """

    name = models.CharField(_("name"))
    module = models.CharField(_("module"))

    def __str__(self):
        return self.name


class ActivityType(RulesModel):
    class ActivityTypes(models.TextChoices):
        EVENT = "event", _("Event")
        GAME = "game", _("Game")
        PRACTICE = "practice", _("Practice")
        OTHER = "other", _("Other")

    name = models.CharField(_("name"), max_length=250, unique=True)
    type = models.CharField(_("type"), max_length=10, choices=ActivityTypes.choices, default=ActivityTypes.OTHER)
    staff_registration_required = models.BooleanField(_("staff registration required"), default=False, help_text=_("If set, requires staff members to also register their attendance for this activity type"))
    logo = models.CharField(_("logo"), max_length=255, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("activity type")
        verbose_name_plural = _("activity types")
        ordering = ["name"]
        rules_permissions = {"add": is_superuser, "view": is_superuser, "change": is_superuser, "delete": is_superuser}

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        match self.type:
            case self.ActivityTypes.EVENT:
                # self.logo = "fa-solid fa-calendar-days"
                self.logo = "calendar_month"
            case self.ActivityTypes.GAME:
                # self.logo = "fa-solid fa-trophy"
                self.logo = "sports_hockey"
            case self.ActivityTypes.PRACTICE:
                # self.logo = "fa-solid fa-hockey-puck"
                self.logo = "fitness_center"
            case self.ActivityTypes.OTHER:
                # self.logo = "fa-solid fa-calendar-days"
                self.logo = "calendar_month"
            case _:
                raise ValueError(_("Invalid activity type"))

        super().save(*args, **kwargs)


class Activity(PolymorphicModel):
    owner = models.ForeignKey("members.Member", on_delete=models.CASCADE, verbose_name=_("owner"))
    teams = models.ManyToManyField("teams.Team", verbose_name=_("teams"), blank=True, related_name="activities")
    members = models.ManyToManyField("members.Member", verbose_name=_("members"), blank=True, related_name="activities", help_text=_("Additional members to add, these are included in addition to the included teams"))

    type = models.ForeignKey(ActivityType, on_delete=models.CASCADE, verbose_name=_("type"))
    start_time = models.DateTimeField(_("start time"))
    end_time = models.DateTimeField(_("end time"), blank=True, null=True)
    gathering_time = models.DateTimeField(_("gathering time"), blank=True, null=True, help_text=_("Date and time when members need to be present at the location"))

    location = models.CharField(_("location"), max_length=255, blank=True, null=True)
    title = models.CharField(_("title"), max_length=255, blank=True, null=True)
    description = models.TextField(_("description"), blank=True, null=True)

    require_registration = models.BooleanField(_("require registration"), default=False, help_text=_("If set, members must register for the activity"))
    registration_deadline = models.DateTimeField(_("registration deadline"), blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("activity")
        verbose_name_plural = _("activities")
        ordering = ["start_time", "end_time"]

    @classmethod
    def for_user(cls, user, include_registrations=True) -> QuerySet["Activity"]:
        """
        Retrieve a list of activities for a specific user. Activities are filtered based on teams
        or members the user is associated with, along with optional inclusion of registration
        details. Only future activities from now are included, and results are ordered by the
        start time.

        :param user: The user for whom activities are being retrieved.
        :type user: User
        :param include_registrations: Whether to include prefetching registration details for
            activities. Defaults to True.
        :type include_registrations: bool
        :return: A list of Activity objects matching the user's criteria.
        """
        members = Member.objects.filter(Q(user=user) | Q(family_members__user=user)).distinct().values_list("pk", flat=True)
        teams = Team.objects.filter(teammembership__season=Season.for_date(), teammembership__member__in=members).distinct().values_list("pk", flat=True)

        activities = cls.objects.not_instance_of(Practice).filter(Q(teams__in=teams) | Q(members__in=members)).filter(start_time__gte=timezone.now()).select_related("type").order_by("start_time").prefetch_related("teams")

        if include_registrations:
            activities = activities.prefetch_related(
                Prefetch("registrations", queryset=Registration.objects.filter(member__in=members).select_related("member", "member__user").order_by("member__user__last_name", "member__user__first_name"), to_attr="my_registrations")
            ).prefetch_related(Prefetch("registrations", queryset=Registration.objects.select_related("member", "member__user").order_by("member__user__last_name", "member__user__first_name"), to_attr="all_registrations"))

        return activities

    def __str__(self):
        if self.title is not None and self.title != "":
            return self.title

        return _("Activity from {start_time} to {end_time}").format(start_time=self.start_time.strftime("%d/%m/%Y %H:%M"), end_time=self.end_time.strftime("%d/%m%Y %H:%M"))

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.end_time is None:
            self.end_time = self.start_time + datetime.timedelta(hours=config.CM_DEFAULT_ACTIVITY_DURATION)

        if self.gathering_time is None:
            self.gathering_time = self.start_time

        if self.registration_deadline is None:
            self.registration_deadline = self.start_time

        super().save(*args, **kwargs)

    def clean(self):
        if isinstance(self, Event) and self.type.type != ActivityType.ActivityTypes.EVENT:
            raise ValueError(_("Events can only be of type 'event'"))

        if isinstance(self, Game) and self.type.type != ActivityType.ActivityTypes.GAME:
            raise ValueError(_("Games can only be of type 'game'"))

        if isinstance(self, (Practice, PracticeOccurrence)) and self.type.type != ActivityType.ActivityTypes.PRACTICE:
            raise ValueError(_("Practices can only be of type 'practice'"))

    @property
    def is_open(self) -> bool:
        """Returns whether the activity is open for registration"""
        if self.require_registration:
            return timezone.now() <= self.registration_deadline

        return True

    @property
    def completed_registrations(self) -> int:
        """Returns the number of completed registrations for the activity"""
        return self.registrations.exclude(response=Registration.ResponseOptions.NO_RESPONSE).count()

    @property
    def total_registrations(self) -> int:
        """Returns the total number of registrations for the activity"""
        return self.registrations.count()

    def generate_registrations(self) -> None:
        """Generates new registrations for the activity based on the current members and teams"""

        if self.require_registration and not isinstance(self, Practice):
            # We don't generate registrations for practices as they are covered through PracticeOccurrence objects
            members = Member.objects.filter(team_memberships__season=Season.for_date(), team_memberships__team__in=self.teams.all())
            if not self.type.staff_registration_required:
                members = members.exclude(team_memberships__role__staff_role=True, team_memberships__role__admin_role=True)

            members = members | self.members.all()

            existing_registrations = self.registrations.all()
            member_pks = set(members.values_list("pk", flat=True))

            for registration in existing_registrations:
                if registration.member.pk not in member_pks:
                    registration.delete()
                else:
                    member_pks.remove(registration.member.pk)

            new_registrations = [Registration(activity=self, member=member) for member in Member.objects.filter(pk__in=member_pks)]
            Registration.objects.bulk_create(new_registrations)


class Event(Activity):
    history = HistoricalRecords(excluded_fields=["created", "updated", "teams", "members", "type", "end_time", "require_registration", "owner", "registration_deadline"])

    class Meta:
        verbose_name = _("event")
        verbose_name_plural = _("events")
        ordering = ["start_time", "end_time", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.title is None or self.title == "":
            self.title = _("Event")

            if self.location is not None and self.location != "":
                self.title = _("Event @ {location}").format(location=self.location)

        super().save(*args, **kwargs)


class Game(Activity):
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, verbose_name=_("team"), related_name="games")
    opponent = models.ForeignKey(Opponent, on_delete=models.CASCADE, verbose_name=_("opponent"), blank=True, null=True, related_name="games")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, verbose_name=_("season"), related_name="games")
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, verbose_name=_("competition"), related_name="games", blank=True, null=True)
    competition_game_id = models.CharField(_("competition id"), max_length=255, blank=True, null=True)

    is_live = models.BooleanField(_("live"), default=False)
    score_team = models.IntegerField(_("score team"), default=0)
    score_opponent = models.IntegerField(_("score opponent"), default=0)

    history = HistoricalRecords(
        excluded_fields=["created", "updated", "is_live", "season", "score_team", "score_opponent", "title", "teams", "type", "end_time", "require_registration", "description", "owner", "registration_deadline", "competition", "competition_id"]
    )

    class Meta:
        verbose_name = _("game")
        verbose_name_plural = _("games")
        ordering = ["start_time", "end_time", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.season = Season.for_date(current_date=self.start_time)

        self.title = _("Game {team}").format(team=self.team.name)

        if self.opponent is not None:
            home_team = self.team if self.is_home_game else self.opponent
            away_team = self.opponent if self.is_home_game else self.team

            self.title = f"{home_team.name} vs. {away_team.name} @ {self.location}"

        super().save(*args, **kwargs)

    @property
    def is_home_game(self) -> bool:
        """Check if the game is a home game"""
        return self.location.lower() == config.CM_CLUB_HOME_LOCATION.lower()

    def update_game_information(self) -> None:
        if self.competition is not None:
            module = importlib.import_module(self.competition.module)
            competition = getattr(module, self.competition.name)

            competition().update_game_information(game=self)


class Practice(Activity):
    recurrences = RecurrenceField(null=True, blank=True, include_dtstart=False)

    history = HistoricalRecords(excluded_fields=["created", "updated", "teams", "members", "type", "end_time", "require_registration", "owner", "registration_deadline", "recurrences"])

    class Meta:
        verbose_name = _("practice")
        verbose_name_plural = _("practices")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title = _("Practice Series")
        super().save(*args, **kwargs)

    def generate_occurrences(self) -> "list[PracticeOccurrence]":
        """
        Synchronizes PracticeOccurrence instances for this Practice series.
        - Updates existing occurrences if their times have changed.
        - Creates new occurrences if needed.
        - Removes occurrences that no longer match the recurrence rule.
        """

        duration = self.end_time - self.start_time
        gathering_time_delay = self.start_time - self.gathering_time
        registration_deadline_delay = self.start_time - self.registration_deadline

        # Generate a list of all expected start_dates
        expected_start_times = set()
        maximum_end_date = self.start_time + datetime.timedelta(days=365)

        if self.recurrences.count() != 0:
            counter = 0
            for dt in self.recurrences.between(self.start_time, maximum_end_date, dtstart=self.start_time, inc=True):
                counter += 1
                expected_start_times.add(dt)

        else:
            expected_start_times.add(self.start_time)

        # Fetch all existing occurrences for this series
        existing_occurrences = {occ.start_time: occ for occ in self.occurrences.filter(is_override=False)}
        occurrences = []

        # Remove any occurrence no longer in the recurrence rule
        occurrences_to_remove = set()
        for occ_start_time, occ in existing_occurrences.items():
            if occ_start_time not in expected_start_times:
                occurrences_to_remove.add(occ.id)

        PracticeOccurrence.objects.filter(id__in=occurrences_to_remove).delete()

        # Create or update occurrences as needed
        for start_time in expected_start_times:
            end_time = start_time + duration
            gathering_time = start_time - gathering_time_delay
            registration_deadline = start_time - registration_deadline_delay
            occurrence = existing_occurrences.get(start_time)

            if occurrence is not None:
                fields_to_update = {
                    "end_time": end_time,
                    "gathering_time": gathering_time,
                    "type": self.type,
                    "location": self.location,
                    "title": self.title,
                    "description": self.description,
                    "require_registration": self.require_registration,
                    "registration_deadline": registration_deadline,
                }

                updated = False
                regenerate_registrations = False

                for field, value in fields_to_update.items():
                    if getattr(occurrence, field) != value:
                        setattr(occurrence, field, value)
                        updated = True

                    if set(occurrence.teams.all()) != self.teams.all():
                        occurrence.teams.set(self.teams.all())
                        regenerate_registrations = True

                    if set(occurrence.members.all()) != self.members.all():
                        occurrence.members.set(self.members.all())
                        regenerate_registrations = True

                    if updated:
                        occurrence.save()

                    if regenerate_registrations:
                        occurrence.generate_registrations()

                occurrences.append(occurrence)

            else:
                occurrence = PracticeOccurrence.objects.get_or_create(
                    series=self,
                    is_override=False,
                    owner=self.owner,
                    start_time=start_time,
                    end_time=end_time,
                    gathering_time=gathering_time,
                    registration_deadline=registration_deadline,
                    type=self.type,
                    location=self.location,
                    title=self.title,
                    description=self.description,
                    require_registration=self.require_registration,
                )[0]
                occurrence.teams.set(self.teams.all())
                occurrence.members.set(self.members.all())
                occurrences.append(occurrence)

        return occurrences


class PracticeOccurrence(Activity):
    series = models.ForeignKey(Practice, on_delete=models.CASCADE, verbose_name=_("series"), related_name="occurrences")
    is_override = models.BooleanField(_("is override"), default=False, help_text=_("If set, this occurrence is an override and not part of the original series"))

    history = HistoricalRecords(excluded_fields=["created", "updated", "teams", "members", "type", "end_time", "require_registration", "owner", "registration_deadline", "series", "is_override"])

    class Meta:
        verbose_name = _("practice occurrence")
        verbose_name_plural = _("practice occurrences")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title = _("Practice")
        super().save(*args, **kwargs)


class RegistrationManager(models.Manager):
    def grouped_by_response(self, buckets=None, order_inside_bucket: bool = True) -> "OrderedDict[str, list[Registration]]":
        return grouped_by_response(self.get_queryset().select_related("member"), buckets, order_inside_bucket)


class Registration(models.Model):
    class ResponseOptions(models.TextChoices):
        NO_RESPONSE = "no_response", _("No response")
        ATTENDING = "attending", _("Attending")
        NOT_ATTENDING = "not_attending", _("Not attending")
        SELECTED = "selected", _("Selected")
        NOT_SELECTED = "not_selected", _("Not selected")

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="registrations", verbose_name=_("activity"))
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="registrations", verbose_name=_("member"))
    response = models.CharField(_("response"), max_length=15, choices=ResponseOptions.choices, default=ResponseOptions.NO_RESPONSE)
    comment = models.TextField(_("comment"), blank=True)

    objects = RegistrationManager()
    history = HistoricalRecords(excluded_fields=["created", "updated"])

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("modified"), auto_now=True)

    class Meta:
        verbose_name = _("registration")
        verbose_name_plural = _("registrations")
        unique_together = ("activity", "member")

    def __str__(self):
        return f"{self.member} // {self.activity.title} ({self.get_response_display()})"

        # return f"{self.member} - {self.activity} ({self.response})"
