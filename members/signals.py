from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Member

User = get_user_model()


@receiver(post_save, sender=User)
def create_member(instance, **kwargs) -> None:
    """Creates a Member instance when a new User is created."""
    Member.objects.get_or_create(user=instance)


@receiver(post_delete, sender=Member)
def delete_associated_user(instance, **kwargs) -> None:
    """Deletes the associated user when the Member is deleted."""
    instance.user.delete()
