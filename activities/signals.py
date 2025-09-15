from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Game


@receiver(post_save, sender=Game)
def game_post_save_handler(instance, **kwargs) -> None:
    instance.teams.set([instance.team])
