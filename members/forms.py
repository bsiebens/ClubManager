from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Member

class MemberForm(forms.ModelForm):
    first_name = forms.CharField(max_length=250, label=_("First Name"))
    last_name = forms.CharField(max_length=250, label=_("Last Name"))
    email = forms.EmailField(label=_("Email"))

    admin = forms.BooleanField(label=_("Admin?"), required=False, help_text=_("If checked will mark this user as a site admin granting "
                                                                                       "them all permissions"))

    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput, required=False)
    password_confirm = forms.CharField(label=_("Confirm Password"), widget=forms.PasswordInput, required=False)

    class Meta:
        model = Member
        fields = ["phone", "emergency_phone", "license", "birthday", "family_members"]
        localized_fields = fields

    def save(self, commit:bool = True) -> Member:
        password = None

        if self.cleaned_data["password"] is not None and self.cleaned_data["password"] != "" and self.cleaned_data["password"] == self.cleaned_data["password_confirm"]:
            password = self.cleaned_data["password"]

        member = Member.create_member(first_name=self.cleaned_data["first_name"], last_name=self.cleaned_data["last_name"],
                                      email=self.cleaned_data["email"], password=password, member=self.instance)

        member.phone = self.cleaned_data["phone"]
        member.emergency_phone = self.cleaned_data["emergency_phone"]
        member.license = self.cleaned_data["license"]
        member.birthday = self.cleaned_data["birthday"]

        if self.cleaned_data["admin"]:
            member.user.is_superuser = True
            member.user.save(update_fields=["is_superuser"])

        member.save(update_fields=["phone", "emergency_phone", "license", "birthday"])
        member.family_members.set(self.cleaned_data["family_members"])

        return member