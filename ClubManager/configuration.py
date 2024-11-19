from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from constance import config
from .forms import ConfigurationForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

def index(request: HttpRequest) -> HttpResponse:
    initial_data = {
        "club_name": config.CLUBMANAGER_CLUB_NAME,
        "club_location": config.CLUBMANAGER_CLUB_LOCATION,
        "club_logo": config.CLUBMANAGER_CLUB_LOGO,
    }

    form = ConfigurationForm(initial=initial_data)

    if request.method == "POST":
        form = ConfigurationForm(request.POST, request.FILES)
        if form.is_valid():
            config.CLUBMANAGER_CLUB_NAME = form.cleaned_data["club_name"]

            if config.CLUBMANAGER_CLUB_LOCATION != form.cleaned_data["club_location"]:
                config.CLUBMANAGER_CLUB_LOCATION = form.cleaned_data["club_location"]

                # TODO Run update on home games to change location to new location

            if form.cleaned_data["club_logo"] is not None:
                # TODO Save logo and updat config
                ...

            messages.success(request=request, message=_("Settings have been saved successfully"))

    return render(request, "configuration/index.html", {"form": form})