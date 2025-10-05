from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Message, MessageReadStatus, ConversationParticipant


@receiver(post_save, sender=Message)
def create_message_read_status(sender, instance, created, **kwargs):
    """
    Automatically create MessageReadStatus records for all active participants
    when a new message is created.

    This signal ensures that every active participant in a conversation gets
    a MessageReadStatus record for tracking whether they've read the message.
    The sender is automatically marked as having read the message.
    """
    if created:
        # Get all active participants in the conversation
        active_participants = ConversationParticipant.objects.filter(conversation=instance.conversation, is_active=True).select_related("user")

        # Create a MessageReadStatus for each participant
        read_statuses = []
        for participant in active_participants:
            read_status = MessageReadStatus(message=instance, user=participant.user, read_at=instance.sent_at if participant.user == instance.sender else None)
            read_statuses.append(read_status)

        # Bulk create for efficiency
        if read_statuses:
            MessageReadStatus.objects.bulk_create(read_statuses, ignore_conflicts=True)
