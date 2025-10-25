import secrets

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Member

User = get_user_model()


@receiver(post_save, sender=User)
def create_member(instance, **kwargs) -> None:
    """Creates a Member instance when a new User is created."""
    member, created = Member.objects.get_or_create(user=instance)
    
    if not member.token:
        member.token = secrets.token_urlsafe(64)
        member.save(update_fields=["token"])
