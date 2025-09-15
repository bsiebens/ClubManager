from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from teams.models import TeamMembership
from .models import Game, Activity, Practice, PracticeOccurrence, Event


@receiver(post_save, sender=Practice)
def practice_post_save_handler(sender, instance, created, **kwargs):
    instance.generate_occurrences()


@receiver(post_save, sender=Activity)
@receiver(post_save, sender=Practice)
@receiver(post_save, sender=Game)
@receiver(post_save, sender=PracticeOccurrence)
@receiver(post_save, sender=Event)
def activity_post_save_handler(sender, instance, created, **kwargs):
    if sender == Game:
        instance.teams.set([instance.team])

    instance.generate_registrations()


@receiver([post_save, post_delete], sender=TeamMembership)
def team_membership_post_save_handler(instance, **kwargs) -> None:
    for activity in Activity.objects.filter(teams=instance.team, start_time__gte=timezone.now()):
        activity.generate_registrations()
