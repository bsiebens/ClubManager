from collections import defaultdict

from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from generic_notifications import send_notification
from django.contrib.auth import get_user_model
from django.db.models import Q
from notifications.notifications import RegistrationNotification, CalendarNotification
from teams.models import TeamMembership, Season
from members.models import Member
from .models import Practice, Event, Game, Activity, PracticeOccurrence, Registration


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
@receiver(post_save, sender=Event)
@receiver(post_save, sender=Game)
@receiver(post_save, sender=PracticeOccurrence)
@receiver(post_save, sender=Registration)
def send_notifications(sender, instance, created, **kwargs) -> None:
    recipients = set()
    notification_text = None
    notification_url = None
    notification_type = None
    send_notification_to_users = False
    notification_subject = None
    users = defaultdict(set)

    if isinstance(instance, Registration) and (instance.response == Registration.ResponseOptions.SELECTED or instance.response == Registration.ResponseOptions.NOT_SELECTED):
        notification_subject = f"{instance.activity.title} ({instance.activity.start_time.strftime('%d/%m/%Y %H:%M')})"
        recipients = {instance.member.user, *[member.user for member in instance.member.family_members.all()]}
        notification_type = RegistrationNotification

        notification_text = _("Status for {member} has been changed to <b>{response}</b>").format(member=instance.member.user.get_full_name(), response=instance.get_response_display().upper())
        notification_url = reverse("clubmanager:calendar")

        if instance.history.latest().prev_record is not None:
            difference = instance.history.latest().diff_against(instance.history.latest().prev_record)
            if "response" in difference.changed_fields:
                send_notification_to_users = True

        else:
            send_notification_to_users = True
            
    if isinstance(instance, (Event, Game, PracticeOccurrence)):
        notification_subject = f"{instance.title} ({instance.start_time.strftime('%d/%m/%Y %H:%M')})"
        notification_type = CalendarNotification
        notification_url = reverse("clubmanager:calendar")
        send_notification_to_users = True
        
        queryset = (
                instance.members.all().select_related("member__user").prefetch_related("member__family_members__user") |
                Member.objects.filter(team_memberships__season=Season.for_date(), team_memberships__team__in=instance.teams.all()).select_related("user").prefetch_related("family_members__user")
        ).distinct()
        
        if hasattr(instance, "registrations") and instance.registrations.count() > 0:
            queryset = instance.registrations.select_related("member__user").prefetch_related("member__family_members__user")
            
        for registration in queryset:
            user = registration.member.user
            family_members = [member.user for member in registration.member.family_members.all()]
            users[user].update(family_members)
            recipients.add(user)
                
        if instance.history.latest().prev_record is None:
            notification_text = _("A new activity for {member} has been added to the calendar.")
        
        else:
            difference = instance.history.latest().diff_against(instance.history.latest().prev_record)
            print(difference.changed_fields)
            if not difference.changed_fields:
                send_notification_to_users = False
                
            notification_text = _("Activity for {member} has been updated: %s changed") % (", ".join(difference.changed_fields))
            
    if send_notification_to_users:
        for recipient in recipients:
            if isinstance(instance, (Event, Game, PracticeOccurrence)):
                for user, family_members in users.items():
                    notification_text = notification_text.format(member=user.get_full_name())
                    send_notification(recipient=user, notification_type=notification_type, target=instance, subject=notification_subject, text=notification_text, url=notification_url)
                
                    for family_member in family_members:
                        send_notification(recipient=family_member, notification_type=notification_type, target=instance, subject=notification_subject, text=notification_text, url=notification_url)
            
            else:
                send_notification(recipient=recipient, notification_type=notification_type, target=instance, subject=notification_subject, text=notification_text, url=notification_url)


@receiver(post_delete, sender=Activity)
def send_delete_notifications(sender, instance, **kwargs) -> None:
    recipients = {instance.member.user, *[member.user for member in instance.member.family_members.all()]}
    notification_subject = f"{instance.activity.title} ({instance.activity.start_time.strftime('%d/%m/%Y %H:%M')})"
    notification_text = _("Activity has been cancelled for {member}.").format(member=instance.member.user.get_full_name())
    notification_url = reverse("clubmanager:calendar")
    notification_type = CalendarNotification

    for recipient in recipients:
        send_notification(recipient=recipient, notification_type=notification_type, target=instance.activity, subject=notification_subject, text=notification_text, url=notification_url)
