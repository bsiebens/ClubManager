from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from generic_notifications import send_notification

from notifications.notifications import RegistrationNotification
from teams.models import TeamMembership
from .models import Practice, Event, Game, Activity, PracticeOccurrence, Registration, ActivityType


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


@receiver(post_save, sender=Activity)
@receiver(post_save, sender=Registration)
def send_notification_to_user(sender, instance, created, **kwargs) -> None:
    if isinstance(instance, Registration) and (instance.response == Registration.ResponseOptions.SELECTED or instance.response == Registration.ResponseOptions.NOT_SELECTED):
        current_state = instance.history.last()
        activity = instance.activity
        activity_title = activity.title
        recipients = {instance.member.user, *[member.user for member in instance.member.family_members.all()]}

        print(recipients)

        if activity.type.type == ActivityType.ActivityTypes.PRACTICE:
            activity_title = _("Practice")

        elif activity.type.type == ActivityType.ActivityTypes.GAME:
            if activity.opponent is not None:
                activity_title = f"{activity.team.name} vs. {activity.opponent.name} @ {activity.location}"
            else:
                activity_title = _("Game {team}").format(team=activity.team.name)

        notification_subject = _("{activity} ({date})").format(activity=activity_title, date=activity.start_time.strftime("%d/%m/%Y %H:%M"))
        notification_text = mark_safe(_("Status for {member} has been changed to <b>{response}</b>").format(member=instance.member.user.get_full_name(), response=instance.get_response_display().upper()))
        notification_url = reverse("clubmanager:calendar")

        if current_state.prev_record is not None:
            difference = current_state.diff_against(current_state.prev_record)

            if "response" in difference.changed_fields:
                for recipient in recipients:
                    send_notification(recipient=recipient, notification_type=RegistrationNotification, target=instance.activity, subject=notification_subject, text=notification_text, url=notification_url)

        else:
            for recipient in recipients:
                send_notification(recipient=recipient, notification_type=RegistrationNotification, target=instance.activity, subject=notification_subject, text=notification_text, url=notification_url)

    else:
        ...
