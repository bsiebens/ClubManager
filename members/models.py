import secrets
import string
from typing import Any

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from rules import is_superuser
from rules.contrib.models import RulesModel


class MemberManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        """All queryset will return the users cached as we almost always need the user object anyway"""
        return super().get_queryset().select_related("user")

class Member(models.Model):
    """Each user has a member profile, containing links to other family members."""

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="member", verbose_name=_("user"))
    notes = models.TextField(blank=True, verbose_name=_("notes"), default="")
    family_members = models.ManyToManyField("self", blank=True)

    birthday = models.DateField(_("birthday"), blank=True, null=True)
    license = models.CharField(_("license"), max_length=50, blank=True, default="")
    password_change_required = models.BooleanField(_("password change required"), default=False, help_text=_("If checked require the user to "
                                                                                                             "change their password at next logon"))

    phone = PhoneNumberField(_("phone number"), blank=True, default="")
    emergency_phone = PhoneNumberField(_("emergency phone number"), blank=True, default="")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = MemberManager()

    class Meta:
        verbose_name = _("member")
        verbose_name_plural = _("members")
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self) -> str:
        return self.user.get_full_name()

    def delete(self, using: Any = None, keep_parents: bool = False) -> tuple:
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        return super().delete(using, keep_parents)

    @classmethod
    def create_member(cls, first_name: str, last_name: str, email: str, password: str | None = None, member: "Member | None" = None) -> "Member":
        """Creates a new member based on the provided details. Will link this to an existing user or create a new one if necessary."""

        if member is not None:
            member.user.first_name = first_name
            member.user.last_name = last_name
            member.user.email = email
            member.user.username = email

            if password is not None or password != "":
                member.user.set_password(password)

        else:
            member = cls()

            try:
                user = get_user_model().objects.get(first_name=first_name, last_name=last_name, username=email, member=None)
            except get_user_model().DoesNotExist:
                user = get_user_model().objects.create(first_name=first_name, last_name=last_name, email=email, username=email)

            initial_password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
            if password is None or password == "":
                password = initial_password
                member.notes = f"Initial password: {password}"
                member.password_change_required = True

            user.set_password(password)

            member.user = user

        if not member.user.is_active:
            member.user.is_active = True

        member.user.save()
        member.save()

        return member
