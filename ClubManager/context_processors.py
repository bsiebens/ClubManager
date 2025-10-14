from constance import config
from django.http import HttpRequest


def constance_configuration(request: HttpRequest) -> dict[str, str]:
    return {"CM_CLUB_LOGO": config.CM_CLUB_LOGO, "CM_CLUB_NAME": config.CM_CLUB_NAME}
