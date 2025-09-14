from typing import TYPE_CHECKING

import rules
from django.contrib.auth.models import AbstractUser

if TYPE_CHECKING:
    from .models import TeamMembership, Season


@rules.predicate
def is_team_admin(user: AbstractUser | None, teammembership: "TeamMembership | None") -> bool:
    """
    Determine if a user is a team admin within a specific team membership context.

    :param user: The user to check for team admin privileges; can be None.
    :param teammembership: The specific team membership to evaluate; can be None.
    :return: A boolean indicating whether the user is a team admin for the given
        team membership.
    """
    from .models import TeamMembership, Season

    if user is None or teammembership is None:
        return False

    return TeamMembership.objects.filter(team=teammembership.team, member__user=user, role__admin_role=True, season=Season.for_date()).exists()
