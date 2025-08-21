from django.urls import re_path
from .consumers import DepartmentChatConsumer

websocket_urlpatterns = [
    re_path(r"^ws/chat/$", DepartmentChatConsumer.as_asgi()),
]
