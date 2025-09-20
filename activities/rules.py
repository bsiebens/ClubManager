import rules
from django.contrib.auth.models import AbstractUser


@rules.predicate
def is_activity_owner(user: AbstractUser | None, activity: "Activity | None") -> bool:  # type: ignore  # noqa: F821
    """Determine if a user is the owner of an activity."""

    if user is not None:
        return activity is not None and (activity.owner == user or user.is_superuser)

    return False
