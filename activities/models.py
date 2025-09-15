from django.db import models
from django.utils.translation import gettext_lazy as _
from rules import is_superuser
from rules.contrib.models import RulesModel

from teams.rules import is_a_team_admin


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

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("activity type")
        verbose_name_plural = _("activity types")
        ordering = ["name"]
        rules_permissions = {"add": is_superuser, "view": is_superuser, "change": is_superuser, "delete": is_superuser}

    def __str__(self):
        return self.name
