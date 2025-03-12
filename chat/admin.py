from django.contrib import admin # type: ignore
from .models import Message, MessageAttachment, OnlineStatus

admin.site.register(Message)
admin.site.register(MessageAttachment)
admin.site.register(OnlineStatus)