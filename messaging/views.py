from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import Conversation, ConversationParticipant, Message


@login_required
def check_messages(request: HttpRequest) -> HttpResponse:
    return render(request, "ClubManager/base.html#messages_icon")


@login_required
@require_POST
def add_message(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    conversation = Conversation.objects.get(pk=request.POST.get("conversation_pk"))
    is_participant = ConversationParticipant.objects.filter(conversation=conversation, user=request.user, is_active=True).exists()

    if is_participant:
        message = Message.objects.create(conversation=conversation, sender=request.user, content=request.POST.get("message"))

        return redirect("clubmanager:messages-conversation", conversation_pk=conversation.pk)

    return redirect("clubmanager:messages")


# class ConversationViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet for managing conversations.
#
#     Provides endpoints for:
#     - Listing user's conversations
#     - Retrieving a specific conversation with messages
#     - Creating private or group conversations
#     - Adding participants to group conversations
#     - Leaving a conversation
#     - Marking messages as read
#     """
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         """Get conversations where the current user is an active participant."""
#         user = self.request.user
#
#         # Base queryset with active participation
#         queryset = Conversation.objects.for_user(user).select_related('created_by')
#
#         # For list view, add unread count and last message
#         if self.action == 'list':
#             queryset = (
#                 queryset
#                 .with_unread_count(user)
#                 .with_last_message()
#             )
#
#         # For detail view, prefetch participants and recent messages
#         if self.action == 'retrieve':
#             queryset = queryset.prefetch_related(
#                 Prefetch(
#                     'participants',
#                     queryset=ConversationParticipant.objects.filter(
#                         is_active=True
#                     ).select_related('user')
#                 ),
#                 Prefetch(
#                     'messages',
#                     queryset=Message.objects.filter(
#                         is_deleted=False
#                     ).select_related('sender').order_by('-sent_at')[:50]
#                 )
#             ).with_unread_count(user)
#
#         return queryset.distinct()
#
#     def get_serializer_class(self):
#         """Return appropriate serializer based on action."""
#         if self.action == 'list':
#             return ConversationListSerializer
#         elif self.action == 'create_private':
#             return CreatePrivateConversationSerializer
#         elif self.action == 'create_group':
#             return CreateGroupConversationSerializer
#         elif self.action == 'add_participant':
#             return AddParticipantSerializer
#         elif self.action == 'mark_as_read':
#             return MarkAsReadSerializer
#         return ConversationDetailSerializer
#
#     def list(self, request, *args, **kwargs):
#         """List all conversations for the current user."""
#         queryset = self.get_queryset().order_by('-updated_at')
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, *args, **kwargs):
#         """Retrieve a specific conversation with messages."""
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, context={'request': request})
#         return Response(serializer.data)
#
#     @action(detail=False, methods=['post'])
#     def create_private(self, request):
#         """
#         Create a private conversation with another user.
#
#         POST /api/conversations/create_private/
#         {
#             "other_user_id": 123
#         }
#         """
#         serializer = self.get_serializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         conversation = serializer.save()
#
#         # Return full conversation details
#         detail_serializer = ConversationDetailSerializer(
#             conversation,
#             context={'request': request}
#         )
#         return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
#
#     @action(detail=False, methods=['post'])
#     def create_group(self, request):
#         """
#         Create a group conversation.
#
#         POST /api/conversations/create_group/
#         {
#             "name": "Group Name",
#             "participant_ids": [1, 2, 3]
#         }
#         """
#         serializer = self.get_serializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         conversation = serializer.save()
#
#         # Return full conversation details
#         detail_serializer = ConversationDetailSerializer(
#             conversation,
#             context={'request': request}
#         )
#         return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
#
#     @action(detail=True, methods=['post'])
#     def add_participant(self, request, pk=None):
#         """
#         Add a participant to a group conversation.
#
#         POST /api/conversations/{id}/add_participant/
#         {
#             "user_id": 123
#         }
#         """
#         conversation = self.get_object()
#
#         # Only allow adding to group conversations
#         if conversation.conversation_type != 'group':
#             return Response(
#                 {'error': 'Can only add participants to group conversations.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         user_id = serializer.validated_data['user_id']
#
#         # Check if user is already a participant
#         existing = ConversationParticipant.objects.filter(
#             conversation=conversation,
#             user_id=user_id
#         ).first()
#
#         if existing:
#             if existing.is_active:
#                 return Response(
#                     {'error': 'User is already a participant.'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             else:
#                 # Reactivate if they had left
#                 existing.is_active = True
#                 existing.left_at = None
#                 existing.save()
#                 return Response({'status': 'User rejoined the conversation.'})
#
#         # Add new participant
#         ConversationParticipant.objects.create(
#             conversation=conversation,
#             user_id=user_id
#         )
#
#         return Response({'status': 'Participant added successfully.'})
#
#     @action(detail=True, methods=['post'])
#     def leave(self, request, pk=None):
#         """
#         Leave a conversation (soft delete).
#
#         POST /api/conversations/{id}/leave/
#         """
#         conversation = self.get_object()
#
#         participant = ConversationParticipant.objects.filter(
#             conversation=conversation,
#             user=request.user,
#             is_active=True
#         ).first()
#
#         if not participant:
#             return Response(
#                 {'error': 'You are not a participant in this conversation.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         participant.leave()
#
#         return Response({'status': 'You have left the conversation.'})
#
#     @action(detail=True, methods=['post'])
#     def mark_as_read(self, request, pk=None):
#         """
#         Mark messages as read in a conversation.
#
#         POST /api/conversations/{id}/mark_as_read/
#         {
#             "message_ids": [1, 2, 3]  // Optional: specific messages
#         }
#         or
#         {
#             "mark_all": true  // Mark all unread messages in conversation
#         }
#         """
#         conversation = self.get_object()
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         user = request.user
#         mark_all = serializer.validated_data.get('mark_all', False)
#         message_ids = serializer.validated_data.get('message_ids', [])
#
#         if mark_all:
#             # Mark all unread messages in this conversation
#             MessageReadStatus.objects.filter(
#                 message__conversation=conversation,
#                 user=user,
#                 read_at__isnull=True
#             ).update(read_at=timezone.now())
#             return Response({'status': 'All messages marked as read.'})
#
#         if message_ids:
#             # Mark specific messages
#             MessageReadStatus.objects.filter(
#                 message_id__in=message_ids,
#                 message__conversation=conversation,
#                 user=user,
#                 read_at__isnull=True
#             ).update(read_at=timezone.now())
#             return Response({'status': f'{len(message_ids)} message(s) marked as read.'})
#
#         return Response(
#             {'error': 'No messages to mark as read.'},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#
#     @action(detail=False, methods=['get'])
#     def unread_count(self, request):
#         """
#         Get total unread message count across all conversations.
#
#         GET /api/conversations/unread_count/
#         """
#         count = MessageReadStatus.objects.filter(
#             user=request.user,
#             read_at__isnull=True,
#             message__is_deleted=False,
#             message__conversation__participants__user=request.user,
#             message__conversation__participants__is_active=True
#         ).count()
#
#         return Response({'unread_count': count})
#
#
# class MessageViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet for managing messages.
#
#     Provides endpoints for:
#     - Listing messages in a conversation
#     - Sending a message
#     - Marking a message as read
#     """
#     permission_classes = [IsAuthenticated]
#     serializer_class = MessageSerializer
#
#     def get_queryset(self):
#         """Get messages in conversations where the user is an active participant."""
#         user = self.request.user
#         conversation_id = self.request.query_params.get('conversation_id')
#
#         queryset = Message.objects.filter(
#             conversation__participants__user=user,
#             conversation__participants__is_active=True,
#             is_deleted=False
#         ).select_related('sender', 'conversation')
#
#         if conversation_id:
#             queryset = queryset.filter(conversation_id=conversation_id)
#
#         return queryset.distinct().order_by('sent_at')
#
#     def list(self, request, *args, **kwargs):
#         """
#         List messages, optionally filtered by conversation.
#
#         GET /api/messages/?conversation_id=123
#         """
#         queryset = self.get_queryset()
#
#         # Optional pagination
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
#
#     @transaction.atomic
#     def create(self, request, *args, **kwargs):
#         """
#         Send a message in a conversation.
#
#         POST /api/messages/
#         {
#             "conversation": 123,
#             "content": "Hello!"
#         }
#         """
#         serializer = self.get_serializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#
#         # Check if user is an active participant
#         conversation_id = serializer.validated_data['conversation'].id
#         is_participant = ConversationParticipant.objects.filter(
#             conversation_id=conversation_id,
#             user=request.user,
#             is_active=True
#         ).exists()
#
#         if not is_participant:
#             return Response(
#                 {'error': 'You are not a participant in this conversation.'},
#                 status=status.HTTP_403_FORBIDDEN
#             )
#
#         # Create the message (signals will handle MessageReadStatus creation)
#         message = serializer.save()
#
#         # Return the created message
#         return Response(
#             MessageSerializer(message, context={'request': request}).data,
#             status=status.HTTP_201_CREATED
#         )
#
#     @action(detail=True, methods=['post'])
#     def mark_read(self, request, pk=None):
#         """
#         Mark a specific message as read.
#
#         POST /api/messages/{id}/mark_read/lass ConversationViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet for managing conversations.
#
#     Provides endpoints for:
#     - Listing user's conversations
#     - Retrieving a specific conversation with messages
#     - Creating private or group conversations
#     - Adding participants to group conversations
#     - Leaving a conversation
#     - Marking messages as read
#     """
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         """Get conversations where the current user is an active participant."""
#         user = self.request.user
#
#         # Base queryset with active participation
#         queryset = Conversation.objects.for_user(user).select_related('created_by')
#
#         # For list view, add unread count and last message
#         if self.action == 'list':
#             queryset = (
#                 queryset
#                 .with_unread_count(user)
#                 .with_last_message()
#             )
#
#         # For detail view, prefetch participants and recent messages
#         if self.action == 'retrieve':
#             queryset = queryset.prefetch_related(
#                 Prefetch(
#                     'participants',
#                     queryset=ConversationParticipant.objects.filter(
#                         is_active=True
#                     ).select_related('user')
#                 ),
#                 Prefetch(
#                     'messages',
#                     queryset=Message.objects.filter(
#                         is_deleted=False
#                     ).select_related('sender').order_by('-sent_at')[:50]
#                 )
#             ).with_unread_count(user)
#
#         return queryset.distinct()
#
#     def get_serializer_class(self):
#         """Return appropriate serializer based on action."""
#         if self.action == 'list':
#             return ConversationListSerializer
#         elif self.action == 'create_private':
#             return CreatePrivateConversationSerializer
#         elif self.action == 'create_group':
#             return CreateGroupConversationSerializer
#         elif self.action == 'add_participant':
#             return AddParticipantSerializer
#         elif self.action == 'mark_as_read':
#             return MarkAsReadSerializer
#         return ConversationDetailSerializer
#
#     def list(self, request, *args, **kwargs):
#         """List all conversations for the current user."""
#         queryset = self.get_queryset().order_by('-updated_at')
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, *args, **kwargs):
#         """Retrieve a specific conversation with messages."""
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, context={'request': request})
#         return Response(serializer.data)
#
#     @action(detail=False, methods=['post'])
#     def create_private(self, request):
#         """
#         Create a private conversation with another user.
#
#         POST /api/conversations/create_private/
#         {
#             "other_user_id": 123
#         }
#         """
#         serializer = self.get_serializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         conversation = serializer.save()
#
#         # Return full conversation details
#         detail_serializer = ConversationDetailSerializer(
#             conversation,
#             context={'request': request}
#         )
#         return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
#
#     @action(detail=False, methods=['post'])
#     def create_group(self, request):
#         """
#         Create a group conversation.
#
#         POST /api/conversations/create_group/
#         {
#             "name": "Group Name",
#             "participant_ids": [1, 2, 3]
#         }
#         """
#         serializer = self.get_serializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         conversation = serializer.save()
#
#         # Return full conversation details
#         detail_serializer = ConversationDetailSerializer(
#             conversation,
#             context={'request': request}
#         )
#         return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
#
#     @action(detail=True, methods=['post'])
#     def add_participant(self, request, pk=None):
#         """
#         Add a participant to a group conversation.
#
#         POST /api/conversations/{id}/add_participant/
#         {
#             "user_id": 123
#         }
#         """
#         conversation = self.get_object()
#
#         # Only allow adding to group conversations
#         if conversation.conversation_type != 'group':
#             return Response(
#                 {'error': 'Can only add participants to group conversations.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         user_id = serializer.validated_data['user_id']
#
#         # Check if user is already a participant
#         existing = ConversationParticipant.objects.filter(
#             conversation=conversation,
#             user_id=user_id
#         ).first()
#
#         if existing:
#             if existing.is_active:
#                 return Response(
#                     {'error': 'User is already a participant.'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             else:
#                 # Reactivate if they had left
#                 existing.is_active = True
#                 existing.left_at = None
#                 existing.save()
#                 return Response({'status': 'User rejoined the conversation.'})
#
#         # Add new participant
#         ConversationParticipant.objects.create(
#             conversation=conversation,
#             user_id=user_id
#         )
#
#         return Response({'status': 'Participant added successfully.'})
#
#     @action(detail=True, methods=['post'])
#     def leave(self, request, pk=None):
#         """
#         Leave a conversation (soft delete).
#
#         POST /api/conversations/{id}/leave/
#         """
#         conversation = self.get_object()
#
#         participant = ConversationParticipant.objects.filter(
#             conversation=conversation,
#             user=request.user,
#             is_active=True
#         ).first()
#
#         if not participant:
#             return Response(
#                 {'error': 'You are not a participant in this conversation.'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         participant.leave()
#
#         return Response({'status': 'You have left the conversation.'})
#
#     @action(detail=True, methods=['post'])
#     def mark_as_read(self, request, pk=None):
#         """
#         Mark messages as read in a conversation.
#
#         POST /api/conversations/{id}/mark_as_read/
#         {
#             "message_ids": [1, 2, 3]  // Optional: specific messages
#         }
#         or
#         {
#             "mark_all": true  // Mark all unread messages in conversation
#         }
#         """
#         conversation = self.get_object()
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         user = request.user
#         mark_all = serializer.validated_data.get('mark_all', False)
#         message_ids = serializer.validated_data.get('message_ids', [])
#
#         if mark_all:
#             # Mark all unread messages in this conversation
#             MessageReadStatus.objects.filter(
#                 message__conversation=conversation,
#                 user=user,
#                 read_at__isnull=True
#             ).update(read_at=timezone.now())
#             return Response({'status': 'All messages marked as read.'})
#
#         if message_ids:
#             # Mark specific messages
#             MessageReadStatus.objects.filter(
#                 message_id__in=message_ids,
#                 message__conversation=conversation,
#                 user=user,
#                 read_at__isnull=True
#             ).update(read_at=timezone.now())
#             return Response({'status': f'{len(message_ids)} message(s) marked as read.'})
#
#         return Response(
#             {'error': 'No messages to mark as read.'},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#
#     @action(detail=False, methods=['get'])
#     def unread_count(self, request):
#         """
#         Get total unread message count across all conversations.
#
#         GET /api/conversations/unread_count/
#         """
#         count = MessageReadStatus.objects.filter(
#             user=request.user,
#             read_at__isnull=True,
#             message__is_deleted=False,
#             message__conversation__participants__user=request.user,
#             message__conversation__participants__is_active=True
#         ).count()
#
#         return Response({'unread_count': count})
#
#
# class MessageViewSet(viewsets.ModelViewSet):
#     """
#
#         """
#         message = self.get_object()
#         message.mark_as_read_by(request.user)
#
#         return Response({'status': 'Message marked as read.'})
#
#     @action(detail=False, methods=['get'])
#     def unread(self, request):
#         """
#         Get all unread messages for the current user.
#
#         GET /api/messages/unread/
#         """
#         queryset = Message.objects.unread_for_user(request.user).select_related(
#             'sender', 'conversation'
#         ).order_by('-sent_at')
#
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
