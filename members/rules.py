from typing import Optional

import rules
from django.contrib.auth.models import AbstractUser


@rules.predicate
def is_member_manager(user: Optional[AbstractUser]) -> bool:
    return user.has_perm("members.member_manager")
