# Messaging App Documentation

## Overview

A comprehensive Django messaging application that supports:
- Private conversations (1-on-1 messaging)
- Group conversations (multiple participants)
- Individual read/unread status tracking for each user
- Unread message counts per user
- Soft-delete functionality (users can leave conversations without deleting for others)

## Models

### Conversation
Represents a chat (private or group).
- `conversation_type`: 'private' or 'group'
- `name`: Group name (required for group chats)
- `created_by`: User who created the conversation
- `created_at`, `updated_at`: Timestamps

### ConversationParticipant
Tracks user membership in conversations with soft-delete support.
- `conversation`: FK to Conversation
- `user`: FK to User
- `joined_at`: When user joined
- `left_at`: When user left (null if still active)
- `is_active`: Boolean indicating if user is still in conversation

### Message
Individual messages in conversations.
- `conversation`: FK to Conversation
- `sender`: FK to User
- `content`: Message text
- `sent_at`: Timestamp
- `is_deleted`: Soft-delete flag

### MessageReadStatus
Tracks read/unread status per user per message.
- `message`: FK to Message
- `user`: FK to User
- `read_at`: Timestamp when read (null if unread)

## API Endpoints

### Conversations

#### List all conversations
```
GET /api/messaging/conversations/
```
Returns all conversations where the user is an active participant, with unread counts.

#### Get conversation details
```
GET /api/messaging/conversations/{id}/
```
Returns conversation details with participants and recent messages (last 50).

#### Create private conversation
```
POST /api/messaging/conversations/create_private/
{
    "other_user_id": 123
}
```
Creates or retrieves a private conversation with another user.

#### Create group conversation
```
POST /api/messaging/conversations/create_group/
{
    "name": "Team Chat",
    "participant_ids": [1, 2, 3, 4]
}
```
Creates a new group conversation with specified participants (creator is auto-included).

#### Add participant to group
```
POST /api/messaging/conversations/{id}/add_participant/
{
    "user_id": 5
}
```
Adds a user to an existing group conversation.

#### Leave conversation
```
POST /api/messaging/conversations/{id}/leave/
```
Soft-deletes the user from the conversation (messages remain for others).

#### Mark messages as read
```
POST /api/messaging/conversations/{id}/mark_as_read/
{
    "mark_all": true
}
```
or
```
POST /api/messaging/conversations/{id}/mark_as_read/
{
    "message_ids": [1, 2, 3]
}
```
Marks messages as read for the current user.

#### Get total unread count
```
GET /api/messaging/conversations/unread_count/
```
Returns total unread message count across all conversations.

### Messages

#### List messages
```
GET /api/messaging/messages/?conversation_id=123
```
Lists messages in a specific conversation (or all accessible messages if no filter).

#### Send message
```
POST /api/messaging/messages/
{
    "conversation": 123,
    "content": "Hello everyone!"
}
```
Sends a new message in a conversation.

#### Mark specific message as read
```
POST /api/messaging/messages/{id}/mark_read/
```
Marks a single message as read.

#### Get all unread messages
```
GET /api/messaging/messages/unread/
```
Returns all unread messages for the current user.

## Key Features

### Individual Read Status Tracking
When a message is sent, a `MessageReadStatus` record is automatically created for each active participant in the conversation. This allows tracking who has read each message individually.

### Unread Count
Get unread counts at multiple levels:
- Per conversation: Included in conversation list endpoint
- Total across all conversations: `/api/messaging/conversations/unread_count/`
- Per message: Check `is_read_by_current_user` field in message response

### Soft Delete / Leave Conversation
When a user leaves a conversation:
- Their `ConversationParticipant.is_active` is set to `False`
- `left_at` timestamp is recorded
- Messages remain visible to other participants
- User no longer sees the conversation in their list
- User can be re-added to the same conversation later

### Efficient Queries
Custom managers and querysets provide optimized database queries:
- `Conversation.objects.for_user(user)`: Get user's active conversations
- `Conversation.objects.with_unread_count(user)`: Annotate with unread counts
- `Message.objects.unread_for_user(user)`: Get unread messages
- Proper use of `select_related` and `prefetch_related` for performance

## Admin Interface

All models are registered in Django admin with:
- Inline editing of related objects
- Read/unread status indicators
- Participant management
- Message previews
- Search and filtering capabilities

## Usage Examples

### Python/Django Shell

```python
from django.contrib.auth import get_user_model
from messaging.models import Conversation, Message

User = get_user_model()
user1 = User.objects.get(id=1)
user2 = User.objects.get(id=2)

# Create a private conversation
conversation, created = Conversation.objects.get_or_create_private_conversation(user1, user2)

# Send a message
message = Message.objects.create(
    conversation=conversation,
    sender=user1,
    content="Hello!"
)

# Check unread count for user2
unread_count = conversation.messages.filter(
    readstatus__user=user2,
    readstatus__read_at__isnull=True
).count()

# Mark message as read
message.mark_as_read_by(user2)

# User leaves conversation (soft delete)
participant = conversation.participants.get(user=user2)
participant.leave()
```

### JavaScript/Frontend

```javascript
// Get all conversations
fetch('/api/messaging/conversations/', {
    headers: {
        'Authorization': 'Bearer YOUR_TOKEN'
    }
})
.then(response => response.json())
.then(data => console.log(data));

// Send a message
fetch('/api/messaging/messages/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN'
    },
    body: JSON.stringify({
        conversation: 123,
        content: 'Hello!'
    })
})
.then(response => response.json())
.then(data => console.log(data));

// Mark all messages in conversation as read
fetch('/api/messaging/conversations/123/mark_as_read/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN'
    },
    body: JSON.stringify({
        mark_all: true
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Next Steps

1. Run migrations:
   ```bash
   python manage.py makemigrations messaging
   python manage.py migrate
   ```

2. (Optional) Add permissions using django-rules if needed
3. (Optional) Add WebSocket support for real-time messaging using Django Channels
4. (Optional) Add file attachment support
5. (Optional) Add message editing and deletion features
6. (Optional) Add typing indicators
7. (Optional) Add message reactions

## Database Indexes

The models include strategic indexes for performance:
- `Conversation`: `updated_at`, `conversation_type`
- `ConversationParticipant`: `(conversation, is_active)`, `(user, is_active)`
- `Message`: `(conversation, sent_at)`, `(conversation, is_deleted, sent_at)`
- `MessageReadStatus`: `(user, read_at)`, `(message, user)`

## Security Considerations

- All API endpoints require authentication (`IsAuthenticated` permission)
- Users can only access conversations they're active participants in
- Users can only send messages to conversations they're in
- MessageReadStatus records are automatically created (can't be manually added via admin)
- Proper queryset filtering ensures data isolation between users
