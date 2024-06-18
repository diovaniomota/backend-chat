from rest_framework.response import Response

from django.db.models import Q
from django.utils.timezone import now

from chats.views.base import BaseView
from chats.models import Chat
from chats.serializers import ChatSerializer

from core.socket import socket


class ChatsView(BaseView):
    def get(self, request):
        chats = Chat.objects.filter(
            Q(from_user_id=request.user.id) |  Q(to_user_id=request.user.id),
            deleted_at__isnull=True
        ).order_by('-viewed_at').all()

        serializer = ChatSerializer(
            chats,
            context={'user_id': request .user.id},
            many=True
        )

        return Response({
            'chats: serializer.data'
        })
    
    def post(self, request):
        email = request.data.get('email')

        # Getting user
        user = self.get__user(email=email)

        #Checking if chat already exists
        chat = self.has_existing_chat(user_id=request.user.id, to_user=user.id)

        #creating chat

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
        return Response({
            'chat': chat
        })
