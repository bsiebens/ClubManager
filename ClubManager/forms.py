from django import forms
from django.utils.translation import gettext_lazy as _


class ConfigurationForm(forms.Form):
    """Form instance that holds configuration values for the application."""

    club_name = forms.CharField(label=_("Club Name"), max_length=250)
    club_location = forms.CharField(label=_("Home Game Location"), max_length=250, help_text=_("Changing this setting will set a new home game "
                                                                                               "location and will update already existing games"))
    club_logo = forms.ImageField(label=_("Club Logo"), required=False)