from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Member

User = get_user_model()


@receiver(post_save, sender=User)
def create_member(instance, **kwargs):
    Member.objects.get_or_create(user=instance)
