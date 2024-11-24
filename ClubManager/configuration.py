from pathlib import Path

from constance import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from .forms import ConfigurationForm


@login_required
@user_passes_test(lambda u: u.is_superuser)
def index(request: HttpRequest) -> HttpResponse:
    initial_data = {
        "club_name": config.CLUBMANAGER_CLUB_NAME,
        "club_location": config.CLUBMANAGER_CLUB_LOCATION,
        "club_logo": config.CLUBMANAGER_CLUB_LOGO,
        "club_enable_teams": config.CLUBMANAGER_ENABLE_TEAMS,
    }

    form = ConfigurationForm(initial=initial_data)

    if request.method == "POST":
        form = ConfigurationForm(request.POST, request.FILES)
        if form.is_valid():
            config.CLUBMANAGER_CLUB_NAME = form.cleaned_data["club_name"]
            config.CLUBMANAGER_CLUB_LOCATION = form.cleaned_data["club_location"]
            config.CLUBMANAGER_ENABLE_TEAMS = form.cleaned_data["club_enable_teams"]

            if form.cleaned_data["club_logo"] is not None:
                default_storage.save(Path(settings.STATIC_ROOT / form.cleaned_data["club_logo"].name), form.cleaned_data["club_logo"])
                config.CLUBMANAGER_CLUB_LOGO = form.cleaned_data["club_logo"].name

            messages.success(request=request, message=_("Settings have been saved successfully"))

    return render(request, "configuration/index.html", {"form": form})
