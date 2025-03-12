"""
ASGI config for collegecue_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application # type: ignore
from channels.routing import ProtocolTypeRouter, URLRouter # type: ignore
from channels.auth import AuthMiddlewareStack # type: ignore
from chat.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collegecue_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
   "websocket": AuthMiddlewareStack(
       URLRouter(
           websocket_urlpatterns
       )
   ),
})




"""import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collegecue_project.settings')

application = get_asgi_application()"""
