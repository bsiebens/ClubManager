#  Copyright (c) ClubManager - Bernard Siebens 2024.

from django.db import models
from django.utils.translation import gettext_lazy as _
from rules import is_superuser
from rules.contrib.models import RulesModel


class Season(RulesModel):
    """A season groups information together in time."""
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))

    class Meta:
        verbose_name = _("season")
        verbose_name_plural = _("seasons")
        ordering = ["start_date"]
        rules_permissions = {
            "add": is_superuser, "view": is_superuser, "change": is_superuser, "delete": is_superuser
        }

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"