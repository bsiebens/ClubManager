import rules
from django.contrib.auth.models import AbstractUser


@rules.predicate
def is_activity_owner(user: AbstractUser | None, activity: "Activity | None") -> bool:  # type: ignore  # noqa: F821
    """Determine if a user is the owner of an activity."""

    if user is not None:
        return activity is not None and (activity.owner == user or user.is_superuser)

    return False

@rules.predicate
def can_modify_registration_for_member(user: AbstractUser | None, member: "Member | None") -> bool: # type: ignore  # noqa: F821
    """Determine if a user can modify a registration for a given member."""
    
    if user is not None:
        if user.is_superuser:
            return True
        
        if member is not None:
            if user == member.user:
                return True
            
            if user in member.family_members.all():
                return True
        
    return False

rules.add_rule("can_modify_registration_for_member", can_modify_registration_for_member)