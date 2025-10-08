# chat/urls.py

from django.urls import path
from .views import handle_chat_bot_request, load_chat_bot_base_configuration, debug_pinecone_status

urlpatterns = [
    path('chat-bot/', handle_chat_bot_request, name='chat-bot'),
    path('chat-bot-config/', load_chat_bot_base_configuration, name='chat-bot-config'),
    path('debug-pinecone/', debug_pinecone_status, name='debug-pinecone')
]
