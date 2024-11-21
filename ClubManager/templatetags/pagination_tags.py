#  Copyright (c) 2024. https://github.com/bsiebens/ClubManager

from django import template
from django.http import HttpRequest

# from teams.models import Season

register = template.Library()


@register.simple_tag
def url_replace(
    request: HttpRequest,
    field: str,
    value: str | int,
    default_field: str | None = None,
    default_value: str | int | None = None,
) -> str:
    """Updates the given field in the GET parameters with the supplied value. If field does not exist, it is added."""
    dict_ = request.GET.copy()
    dict_[field] = value

    if default_field is not None and default_field not in dict_.keys():
        dict_[default_field] = default_value

    return dict_.urlencode()


# @register.simple_tag
# def url_replace_with_season(
#     request: HttpRequest,
#     field: str,
#     value: str | int,
#     default_field: str | None = None,
#     default_value: str | int | None = None,
# ) -> str:
#     """Updates the given field in the GET parameters with the supplied value. If field does not exist, it is added."""
#     dict_ = request.GET.copy()
#     dict_[field] = value
#
#     season = Season.get_season_id()
#     dict_["season"] = season
#
#     if default_field is not None and default_field not in dict_.keys():
#         dict_[default_field] = default_value
#
#     return dict_.urlencode()


# @register.simple_tag
# def url_replace_with_season_dates(
#     request: HttpRequest,
#     field: str,
#     value: str | int,
#     default_field: str | None = None,
#     default_value: str | int | None = None,
# ) -> str:
#     """Updates the given field in the GET parameters with the supplied value. If field does not exist, it is added."""
#     dict_ = request.GET.copy()
#     dict_[field] = value
#
#     season = Season.get_season()
#     dict_["start_date"] = season.start_date
#     dict_["end_date"] = season.end_date
#
#     if default_field is not None and default_field not in dict_.keys():
#         dict_[default_field] = default_value
#
#     return dict_.urlencode()