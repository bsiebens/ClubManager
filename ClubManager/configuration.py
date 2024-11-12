from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from constance import config

def index(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        ...

    return render(request, "configuration/index.html")