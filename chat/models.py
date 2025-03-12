from django.db import models # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.utils.timezone import now # type: ignore

class Message(models.Model):
    sender_email = models.EmailField()
    recipient_email = models.EmailField()
    sender_model = models.CharField(max_length=50)
    recipient_model = models.CharField(max_length=50)
    subject = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    attachments = models.ManyToManyField('MessageAttachment', related_name='messages', blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender_email} to {self.recipient_email} on {self.timestamp}"

    @staticmethod
    def get_all_messages():
        """Fetch all messages."""
        return Message.objects.all()

    @staticmethod
    def get_unread_messages():
        """Fetch unread messages."""
        return Message.objects.filter(is_read=False)

    @staticmethod
    def get_read_messages():
        """Fetch read messages."""
        return Message.objects.filter(is_read=True)

class MessageAttachment(models.Model):
    file_url = models.URLField(max_length=500, default="https://res.cloudinary.com/your-cloud-name/image/upload/vdefault/default_file_placeholder.png")
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment {self.original_name} uploaded on {self.uploaded_at}"


class OnlineStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="online_status")
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"

