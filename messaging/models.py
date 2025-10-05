from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import OuterRef, Subquery
from django.utils.translation import gettext_lazy as _


class ConversationQuerySet(models.QuerySet):
    """Custom QuerySet for a Conversation model with optimized queries."""

    def for_user(self, user):
        """Get all conversations where the user is an active participant."""
        return self.filter(participants__user=user, participants__is_active=True).distinct()

    def with_unread_count(self, user):
        """Annotate conversations with unread message count for a specific user."""
        from django.db.models import Count, Q

        return self.annotate(unread_count=Count("messages__readstatus", filter=Q(messages__readstatus__user=user, messages__readstatus__read_at__isnull=True, messages__is_deleted=False)))

    def with_last_message(self):
        """Annotate conversations with their last message."""
        last_message = Message.objects.filter(conversation=OuterRef("pk"), is_deleted=False).order_by("-sent_at")

        return self.annotate(last_message_content=Subquery(last_message.values("content")[:1]), last_message_time=Subquery(last_message.values("sent_at")[:1]))


class ConversationManager(models.Manager):
    """Custom manager for a Conversation model."""

    def get_queryset(self):
        return ConversationQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def with_unread_count(self, user):
        return self.get_queryset().with_unread_count(user)

    def with_last_message(self):
        return self.get_queryset().with_last_message()

    def get_or_create_private_conversation(self, user1, user2):
        """
        Get or create a private conversation between two users.

        Args:
            user1: First user
            user2: Second user

        Returns:
            tuple: (Conversation instance, created boolean)
        """
        if user1 == user2:
            raise ValidationError("Cannot create a conversation with yourself")

        # Try to find existing private conversation between these two users
        existing = self.filter(conversation_type="private", participants__user=user1).filter(participants__user=user2).distinct().first()

        if existing:
            # Reactivate both participants if they had left
            ConversationParticipant.objects.filter(conversation=existing, user__in=[user1, user2]).update(is_active=True, left_at=None)
            return existing, False

        # Create a new conversation
        conversation = self.create(conversation_type="private", created_by=user1)

        # Add both participants
        ConversationParticipant.objects.create(conversation=conversation, user=user1)
        ConversationParticipant.objects.create(conversation=conversation, user=user2)

        return conversation, True


class Conversation(models.Model):
    """
    Represents a conversation (private or group chat).

    A conversation can be:
    - Private: Between exactly 2 users
    - Group: Between 2 or more users with a name
    """

    class ConversationTypes(models.TextChoices):
        PRIVATE = "private", _("Private")
        GROUP = "group", _("Group")

    conversation_type = models.CharField(_("conversation type"), max_length=10, choices=ConversationTypes.choices, default=ConversationTypes.PRIVATE)
    name = models.CharField(_("name"), max_length=255, blank=True, help_text=_("Group name (required for group conversations)"))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_conversations", verbose_name=_("created by"))

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ConversationManager()

    class Meta:
        verbose_name = _("conversation")
        verbose_name_plural = _("conversations")
        ordering = ["-updated"]
        indexes = [
            models.Index(fields=["-updated"]),
            models.Index(fields=["conversation_type"]),
        ]

    def __str__(self):
        if self.conversation_type == "group" and self.name:
            return self.name
        elif self.conversation_type == "private":
            participants = self.participants.filter(is_active=True)[:2]
            if participants.count() == 2:
                return f"{participants[0].user.get_full_name()} & {participants[1].user.get_full_name()}"
        return f"Conversation {self.pk}"

    def clean(self):
        """Validate conversation data."""
        if self.conversation_type == "group" and not self.name:
            raise ValidationError({"name": _("Group conversations must have a name.")})

    def get_active_participants(self):
        """Get all active participants in this conversation."""
        return self.participants.filter(is_active=True)

    def add_participant(self, user):
        """Add a user to the conversation or reactivate them if they left."""
        participant, created = ConversationParticipant.objects.get_or_create(conversation=self, user=user, defaults={"is_active": True})
        if not created and not participant.is_active:
            participant.is_active = True
            participant.left_at = None
            participant.save()
        return participant

    def other_participant(self, user):
        """Get the other participant in this conversation."""
        return self.participants.exclude(user=user).first()


class ConversationParticipant(models.Model):
    """
    Tracks user membership in conversations.

    Supports soft-delete: when a user leaves, we set is_active=False and left_at timestamp.
    This preserves the conversation history for other participants.
    """

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="participants", verbose_name=_("conversation"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversation_participations", verbose_name=_("user"))
    joined_at = models.DateTimeField(_("joined at"), auto_now_add=True)
    left_at = models.DateTimeField(_("left at"), null=True, blank=True)
    is_active = models.BooleanField(_("is active"), default=True)

    class Meta:
        verbose_name = _("conversation participant")
        verbose_name_plural = _("conversation participants")
        ordering = ["joined_at"]
        unique_together = [["conversation", "user"]]
        indexes = [
            models.Index(fields=["conversation", "is_active"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        status = "active" if self.is_active else "left"
        return f"{self.user.get_full_name()} in {self.conversation} ({status})"

    def leave(self):
        """Soft-delete: mark the participant as inactive."""
        from django.utils import timezone

        self.is_active = False
        self.left_at = timezone.now()
        self.save()


class MessageQuerySet(models.QuerySet):
    """Custom QuerySet for a Message model."""

    def active(self):
        """Get only non-deleted messages."""
        return self.filter(is_deleted=False)

    def for_user(self, user):
        """Get messages in conversations where the user is an active participant."""
        return self.filter(conversation__participants__user=user, conversation__participants__is_active=True, is_deleted=False)

    def unread_for_user(self, user):
        """Get unread messages for a specific user."""
        return self.filter(readstatus__user=user, readstatus__read_at__isnull=True, is_deleted=False)


class MessageManager(models.Manager):
    """Custom manager for a Message model."""

    def get_queryset(self):
        return MessageQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def unread_for_user(self, user):
        return self.get_queryset().unread_for_user(user)


class Message(models.Model):
    """
    Represents an individual message in a conversation.

    Messages are soft-deleted (is_deleted flag) so that when a user leaves
    a conversation, their messages remain visible to other participants.
    """

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages", verbose_name=_("conversation"))
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages", verbose_name=_("sender"))
    content = models.TextField(_("content"))
    sent_at = models.DateTimeField(_("sent at"), auto_now_add=True)
    is_deleted = models.BooleanField(_("is deleted"), default=False)

    objects = MessageManager()

    class Meta:
        verbose_name = _("message")
        verbose_name_plural = _("messages")
        ordering = ["sent_at"]
        indexes = [
            models.Index(fields=["conversation", "sent_at"]),
            models.Index(fields=["conversation", "is_deleted", "sent_at"]),
            models.Index(fields=["sender", "sent_at"]),
        ]

    def __str__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.sender.get_full_name()}: {preview}"

    def mark_as_read_by(self, user):
        """Mark this message as read by a specific user."""
        from django.utils import timezone

        MessageReadStatus.objects.filter(message=self, user=user, read_at__isnull=True).update(read_at=timezone.now())

    def is_read_by(self, user):
        """Check if this message has been read by a specific user."""
        return self.readstatus.filter(user=user, read_at__isnull=False).exists()


class MessageReadStatus(models.Model):
    """
    Tracks the read / unread status of each message for each participant.

    When a message is sent, a MessageReadStatus record is created for each
    active participant in the conversation. This allows tracking individual
    read status and calculating unread counts per user.
    """

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="readstatus", verbose_name=_("message"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="message_read_statuses", verbose_name=_("user"))
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)

    class Meta:
        verbose_name = _("message read status")
        verbose_name_plural = _("message read statuses")
        unique_together = [["message", "user"]]
        indexes = [
            models.Index(fields=["user", "read_at"]),
            models.Index(fields=["message", "user"]),
        ]

    def __str__(self):
        status = "read" if self.read_at else "unread"
        return f"{self.user.get_full_name()} - {self.message.pk} ({status})"

    @property
    def is_read(self):
        """Check if the message has been read."""
        return self.read_at is not None
