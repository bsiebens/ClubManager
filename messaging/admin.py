from django.contrib import admin
from django.utils.html import format_html

from .models import Conversation, ConversationParticipant, Message, MessageReadStatus


class ConversationParticipantInline(admin.TabularInline):
    """Inline for managing participants in a conversation."""

    model = ConversationParticipant
    extra = 1
    fields = ["user", "joined_at", "left_at", "is_active"]
    readonly_fields = ["joined_at"]
    autocomplete_fields = ["user"]


class MessageInline(admin.TabularInline):
    """Inline for viewing recent messages in a conversation."""

    model = Message
    extra = 0
    fields = ["sender", "content_preview", "sent_at", "is_deleted"]
    readonly_fields = ["sender", "content_preview", "sent_at"]
    can_delete = False
    max_num = 10

    def content_preview(self, obj):
        """Show a preview of the message content."""
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content

    content_preview.short_description = "Content"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin interface for Conversation model."""

    list_display = ["id", "display_name", "conversation_type", "created_by", "participant_count", "message_count", "created", "updated"]
    list_filter = ["conversation_type", "created", "updated"]
    search_fields = ["name", "created_by__username", "created_by__email"]
    readonly_fields = ["created", "updated", "participant_count", "message_count"]
    autocomplete_fields = ["created_by"]
    date_hierarchy = "created"
    inlines = [ConversationParticipantInline, MessageInline]

    fieldsets = (
        (None, {"fields": ("conversation_type", "name", "created_by")}),
        ("Statistics", {"fields": ("participant_count", "message_count", "created", "updated"), "classes": ("collapse",)}),
    )

    def display_name(self, obj):
        """Display the conversation name or participants."""
        return str(obj)

    display_name.short_description = "Name"

    def participant_count(self, obj):
        """Count active participants."""
        count = obj.participants.filter(is_active=True).count()
        return format_html("<strong>{}</strong>", count)

    participant_count.short_description = "Active Participants"

    def message_count(self, obj):
        """Count messages (non-deleted)."""
        count = obj.messages.filter(is_deleted=False).count()
        return format_html("<strong>{}</strong>", count)

    message_count.short_description = "Messages"


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    """Admin interface for ConversationParticipant model."""

    list_display = ["id", "conversation", "user", "is_active", "joined_at", "left_at"]
    list_filter = ["is_active", "joined_at", "left_at"]
    search_fields = ["user__username", "user__email", "conversation__name"]
    readonly_fields = ["joined_at"]
    autocomplete_fields = ["user", "conversation"]
    date_hierarchy = "joined_at"

    fieldsets = (
        (None, {"fields": ("conversation", "user")}),
        ("Status", {"fields": ("is_active", "joined_at", "left_at")}),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related("user", "conversation")


class MessageReadStatusInline(admin.TabularInline):
    """Inline for viewing read status of a message."""

    model = MessageReadStatus
    extra = 0
    fields = ["user", "read_at", "is_read"]
    readonly_fields = ["user", "read_at", "is_read"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""

    list_display = ["id", "conversation", "sender", "content_preview", "sent_at", "is_deleted", "read_count"]
    list_filter = ["is_deleted", "sent_at"]
    search_fields = ["content", "sender__username", "sender__email", "conversation__name"]
    readonly_fields = ["sent_at", "read_count", "unread_count"]
    autocomplete_fields = ["sender", "conversation"]
    date_hierarchy = "sent_at"
    inlines = [MessageReadStatusInline]

    fieldsets = (
        (None, {"fields": ("conversation", "sender", "content")}),
        ("Metadata", {"fields": ("sent_at", "is_deleted", "read_count", "unread_count"), "classes": ("collapse",)}),
    )

    def content_preview(self, obj):
        """Show a preview of the message content."""
        if len(obj.content) > 100:
            return f"{obj.content[:100]}..."
        return obj.content

    content_preview.short_description = "Content"

    def read_count(self, obj):
        """Count how many participants have read this message."""
        count = obj.readstatus.filter(read_at__isnull=False).count()
        total = obj.readstatus.count()
        return format_html("<strong>{}</strong> / {}", count, total)

    read_count.short_description = "Read by"

    def unread_count(self, obj):
        """Count how many participants haven't read this message."""
        count = obj.readstatus.filter(read_at__isnull=True).count()
        return format_html("<strong>{}</strong>", count)

    unread_count.short_description = "Unread"

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related("sender", "conversation")


@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    """Admin interface for MessageReadStatus model."""

    list_display = ["id", "message_preview", "user", "read_status", "read_at"]
    list_filter = ["read_at"]
    search_fields = ["user__username", "user__email", "message__content"]
    readonly_fields = ["message", "user", "read_at"]
    autocomplete_fields = []
    date_hierarchy = "read_at"

    fieldsets = (
        (None, {"fields": ("message", "user")}),
        ("Status", {"fields": ("read_at",)}),
    )

    def message_preview(self, obj):
        """Show a preview of the message."""
        content = obj.message.content
        if len(content) > 50:
            return f"{content[:50]}..."
        return content

    message_preview.short_description = "Message"

    def read_status(self, obj):
        """Display read/unread status with color."""
        if obj.is_read:
            return format_html('<span style="color: green; font-weight: bold;">✓ Read</span>')
        return format_html('<span style="color: orange; font-weight: bold;">○ Unread</span>')

    read_status.short_description = "Status"

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related("user", "message", "message__sender")

    def has_add_permission(self, request):
        """Prevent manual creation (handled by signals)."""
        return False
