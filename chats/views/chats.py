from rest_framework.response import Response
from rest_framework import status

from django.db.models import Q
from django.utils.timezone import now

from chats.views.base import BaseView
from chats.models import Chat
from chats.serializers import ChatSerializer

from core.socket import socket


class ChatsView(BaseView):
    def get(self, request):
        try:
            chats = Chat.objects.filter(
                Q(from_user_id=request.user.id) | Q(to_user_id=request.user.id),
                deleted_at__isnull=True
            ).order_by('-viewed_at').all()

            serializer = ChatSerializer(
                chats,
                context={'user_id': request.user.id},
                many=True
            )

            return Response({'chats': serializer.data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Getting user
            user = self.get_user(email=email)
            
            if not user:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Checking if chat already exists
            chat = self.has_existing_chat(user_id=request.user.id, to_user=user.id)

            # Creating chat
            if not chat:
                chat = Chat.objects.create(
                    from_user=request.user,
                    to_user=user,
                    viewed_at=now(),
                )

                chat = ChatSerializer(
                    chat,
                    context={'user_id': request.user.id}
                ).data

                # Sending chat to user
                socket.emit('update_chat', {
                    "query": {
                        "users": [request.user.id, user.id]
                    }
                })

            return Response({'chat': chat})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatView(BaseView):
    def delete(self, request, chat_id):
        try:
            # Checking if chat belongs to user
            chat = self.chat_belongs_to_user(
                user_id=request.user.id,
                chat_id=chat_id
            )

            if not chat:
                return Response({'error': 'Chat not found or does not belong to user'}, status=status.HTTP_404_NOT_FOUND)

            # Deleting chat
            deleted = Chat.objects.filter(
                id=chat_id,
                deleted_at__isnull=True
            ).update(
                deleted_at=now()
            )

            if deleted:
                # Sending update chat to user
                socket.emit('update_chat', {
                    "type": "delete",
                    "query": {
                        "chat_id": chat_id,
                        "users": [chat.from_user_id, chat.to_user_id]
                    }
                })

            return Response({"success": True})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
