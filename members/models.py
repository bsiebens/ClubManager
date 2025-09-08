from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from rules import is_superuser
from rules.contrib.models import RulesModel

from .rules import is_member_manager


class Member(RulesModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="member", verbose_name=_("user"))
    
    class Meta:
        verbose_name = _("member")
        verbose_name_plural = _("members")
        ordering = ["user__last_name", "user__first_name"]
        rules_permissions = {
            "add": is_superuser | is_member_manager,
            "view": is_superuser | is_member_manager,
            "change": is_superuser | is_member_manager,
            "delete": is_superuser | is_member_manager,
        }
        permissions = [
            ("member_manager", _("Can manage members")),
        ]
    
    def __str__(self):
        return self.user.get_full_name()
