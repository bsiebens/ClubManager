#  Copyright (c) ClubManager - Bernard Siebens 2024.

import rules
from django.contrib.auth.models import AbstractUser


@rules.predicate
def is_team_admin(user: AbstractUser | None) -> bool:
    return False
