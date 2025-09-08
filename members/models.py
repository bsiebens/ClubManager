from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from rules import is_superuser
from rules.contrib.models import RulesModel
from simple_history.models import HistoricalRecords

from .rules import is_member_manager


class MemberManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        """Returns a QuerySet containing all members, loading relevant member information directly from the related user."""
        return super().get_queryset().select_related("user")


class Member(RulesModel):
    """
    Represents a Member associated with a user and their family details.

    :ivar user: The user linked to this Member instance via a one-to-one relationship.
    :ivar family_members: A list of users designated as family members.
    :ivar birthday: The member's date of birth.
    :ivar license: The member's license or unique identifier string.
    :ivar phone_number: The member's primary contact phone number.
    :ivar emergency_phone_number: An emergency contact phone number for the member.
    """
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="member", verbose_name=_("user"))
    family_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="family_members", verbose_name=_("family members"), blank=True)
    
    birthday = models.DateField(_("birthday"), blank=True, null=True)
    license = models.CharField(_("license"), max_length=20, null=True, blank=True)
    
    phone_number = PhoneNumberField(_("phone number"), blank=True, null=True)
    emergency_phone_number = PhoneNumberField(_("emergency phone number"), blank=True, null=True)
    
    objects = MemberManager()
    history = HistoricalRecords()
    
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
    
    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        
        return 1, {"members.Member": 1}
