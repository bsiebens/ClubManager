from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from teams.models import TeamMembership
from .models import Practice, Event, Game, Activity, PracticeOccurrence


@receiver(post_save, sender=Practice)
def generate_practice_occurrences(instance, **kwargs):
    instance.generate_occurrences()


@receiver(post_save, sender=Event)
@receiver(post_save, sender=Game)
def generate_registrations(sender, instance, **kwargs):
    if sender == Game:
        instance.teams.set([instance.team])

    instance.generate_registrations()


@receiver([post_save, post_delete], sender=TeamMembership)
def team_membership_post_save_handler(instance, **kwargs) -> None:
    for activity in Activity.objects.filter(teams=instance.team, start_time__gte=timezone.now()):
        activity.generate_registrations()


@receiver(m2m_changed, sender=Practice.teams.through)
@receiver(m2m_changed, sender=PracticeOccurrence.teams.through)
@receiver(m2m_changed, sender=Event.teams.through)
@receiver(m2m_changed, sender=Game.teams.through)
@receiver(m2m_changed, sender=Practice.members.through)
@receiver(m2m_changed, sender=PracticeOccurrence.members.through)
@receiver(m2m_changed, sender=Event.members.through)
@receiver(m2m_changed, sender=Game.members.through)
def activity_m2m_changed_handler(instance, action, **kwargs) -> None:
    if action in ["post_add", "post_remove", "post_clear"]:
        if isinstance(instance, Practice):
            instance.generate_occurrences()

        instance.generate_registrations()
