from turtle import update
from asgiref.sync import sync_to_async # type: ignore
from django.core.exceptions import ObjectDoesNotExist # type: ignore
from django.db.models import Q # type: ignore
import requests # type: ignore
from .models import Message, MessageAttachment
from login.models import JobSeeker, new_user, CompanyInCharge, UniversityInCharge # type: ignore
from channels.generic.websocket import AsyncJsonWebsocketConsumer # type: ignore
from dateutil import parser # type: ignore
import json
from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
from django.core.mail import send_mail # type: ignore
from django.conf import settings # type: ignore
from .models import OnlineStatus
from django.utils.timezone import now # type: ignore

MODEL_MAPPING = {
    "JobSeeker": JobSeeker,
    "UniversityInCharge": UniversityInCharge,
    "CompanyInCharge": CompanyInCharge,
    "new_user": new_user,
}


@sync_to_async
def save_message(sender_email, recipient_email, sender_model, recipient_model, subject, content):
    return Message.objects.create(
        sender_email=sender_email,
        recipient_email=recipient_email,
        sender_model=sender_model,
        recipient_model=recipient_model,
        subject=subject,
        content=content
    )


@sync_to_async
def save_attachments(message, attachments):
    saved_attachments = []

    for attachment in attachments:
        file_url = attachment.get("url")  
        original_name = attachment.get("original_name") 
        file_type = attachment.get("file_type", "unknown") 

        # print("file_url:", file_url)
        # print("original_name:", original_name)
        # print("file_type:", file_type)

        if not file_url or not original_name:
            raise ValueError("Each attachment must have 'file_url' and 'original_name'.")

        attachment_obj = MessageAttachment.objects.create(
            file_url=file_url,
            original_name=original_name,
            file_type=file_type,
        )
        
        message.attachments.add(attachment_obj)

        saved_attachments.append({
            "url": attachment_obj.file_url,
            "original_name": attachment_obj.original_name,
            "file_type": attachment_obj.file_type,
        })
        
        message.save()

    return saved_attachments


# @sync_to_async
# def get_user_from_db(model_class, email, token_optional=False):
#     if token_optional or email:
#         try:
#             if hasattr(model_class, "email"):
#                 return model_class.objects.get(email=email)
#             else:
#                 return model_class.objects.get(official_email=email)
#         except model_class.DoesNotExist:
#             raise ObjectDoesNotExist("User not found")
#     raise ObjectDoesNotExist("Invalid email or token")

@sync_to_async
def get_user_from_db(model_class, email, token_optional=False):
    if token_optional or email:
        try:
            email_field = "email" if hasattr(model_class, "email") else "official_email"
            return model_class.objects.get(**{email_field: email})
        except model_class.DoesNotExist:
            raise ObjectDoesNotExist("User not found")
    raise ObjectDoesNotExist("Invalid email or token")



async def get_attachments_for_message(message):
    try:
        attachments = await sync_to_async(list)(message.attachments.all())
        # print("Fetched Attachments:", attachments)
        
        return [
            {
                "original_name": attachment.original_name,
                "url": attachment.file_url,
                "file_type": attachment.file_type,

            }
            for attachment in attachments

        ]
    
    except Exception as e:
        print(f"Error retrieving attachments: {e}")
        return []


@sync_to_async
def set_online_status(user_email, is_online, user_model):
    try:
        # Ensure the email is valid
        if not user_email:
            print("Invalid email provided for online status update.")
            return None

        status, created = OnlineStatus.objects.update_or_create(
            email=user_email,
            defaults={'is_online': is_online}
        )
        print(f"User online status updated: {user_email} -> {is_online}")
        return status  

    except Exception as e:
        print(f"Error in set_online_status: {e}")
        return None

    

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_email = self.scope["url_route"]["kwargs"].get("user_email")
        self.user_model = self.scope["url_route"]["kwargs"].get("user_model")

        if not self.user_model or self.user_model not in MODEL_MAPPING:
            await self.close(code=4001)
            return

        try:
            model_class = MODEL_MAPPING[self.user_model]
            self.user = await get_user_from_db(model_class, self.user_email, token_optional=True)
            await set_online_status(self.user_email, is_online=True, user_model=self.user_model)
        except ObjectDoesNotExist:
            await self.close(code=4002)
            return

        self.group_name = f"user_{self.user_email.replace('@', '_at_').replace('.', '_dot_')}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await set_online_status(self.user_email, is_online=False, user_model=self.user_model)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        action = content.get("action")
        if action == "send_message":
            await self.handle_send_message(content)
        elif action == "get_messages":
            await self.handle_get_messages(content)
        elif action == "ping":
            await self.send_json({"action": "pong"})
        else:
            await self.send_json({"error": "Invalid action"})

    async def handle_get_messages(self, content):
        recipient_email = content.get("recipient_email")
        recipient_model = content.get("recipient_model")
        sender_email = content.get("sender_email", self.user_email)
        since_timestamp = content.get("since_timestamp")

        if not recipient_email or not recipient_model:
            await self.send_json({"error": "Recipient details are required"})
            return

        try:
            messages_query = Message.objects.filter(
                Q(sender_email=sender_email, recipient_email=recipient_email) |
                Q(sender_email=recipient_email, recipient_email=sender_email)
            ).order_by("-timestamp")

            if since_timestamp:
                since_dt = parser.parse(since_timestamp)
                messages_query = messages_query.filter(timestamp__gt=since_dt)

            messages = await sync_to_async(list)(messages_query)

            if messages:
                message_data = []
                for message in messages:
                    attachments = await get_attachments_for_message(message)
                    message_data.append({
                        "id": message.id,
                        "sender_email": message.sender_email,
                        "recipient_email": message.recipient_email,
                        "sender_model": message.sender_model,
                        "recipient_model": message.recipient_model,
                        "subject": message.subject or "",
                        "content": message.content or "",
                        "timestamp": message.timestamp.isoformat(),
                        "attachments": attachments,
                    })

                await self.send_json({
                    "message": "Messages retrieved successfully",
                    "data": message_data,
                })
            else:
                await self.send_json({
                    "message": "No messages found",
                    "data": [],
                })

        except Exception as e:
            await self.send_json({"error": f"An error occurred: {str(e)}"})

    async def handle_send_message(self, content):
        sender_email = self.user_email
        recipient_email = content.get("recipient_email")
        recipient_model = content.get("recipient_model")
        message_content = content.get("content", "").strip()
        subject = content.get("subject", "").strip()
        attachments = content.get("attachments", [])

        if not recipient_email or not recipient_model:
            await self.send_json({"error": "Recipient details are required"})
            return

        if recipient_model not in MODEL_MAPPING:
            await self.send_json({"error": "Invalid recipient model"})
            return

        try:
            recipient_class = MODEL_MAPPING[recipient_model]
            _ = await self.validate_user(recipient_class, None, recipient_email, token_optional=True)
        except ObjectDoesNotExist:
            await self.send_json({"error": "Recipient not found"})
            return

        if not message_content and not attachments:
            await self.send_json({"error": "Either content or attachments must be provided"})
            return

        try:
            message = await save_message(
                sender_email, recipient_email, self.user_model, recipient_model, subject, message_content
            )

            attachment_details = []
            if attachments:
                attachment_details = await save_attachments(message, attachments)

            response_data = {
                "id": message.id,
                "sender_email": sender_email,
                "recipient_email": recipient_email,
                "subject": message.subject,
                "content": message.content,
                "attachments": attachment_details,
                "timestamp": message.timestamp.isoformat(),
            }

            recipient_group = f"user_{recipient_email.replace('@', '_at_').replace('.', '_dot_')}"
            await self.channel_layer.group_send(
                recipient_group,
                {
                    "type": "chat_message",
                    "message": response_data,
                },
            )

            notification_group = f"notifications_{recipient_email.replace('@', '_at_').replace('.', '_dot_')}"
            await self.channel_layer.group_send(
                notification_group,
                {
                    "type": "send_notification",
                    "message": f"You have received a new message from {sender_email}",
                },
            )

            recipient_status = await sync_to_async(lambda: OnlineStatus.objects.filter(email=recipient_email).first())()

            if recipient_status is None or not recipient_status.is_online:
                print(f"Recipient {recipient_email} online status: {recipient_status}")
                
                email_content = f"You have received a new message from {sender_email}.\n\n"

                if subject:
                    email_content += f"Subject: {subject}\n"

                email_content += f"Message: {message_content}\n"

                if attachment_details:
                    attachment_filenames = "\n".join([attachment["original_name"] for attachment in attachment_details])
                    email_content += f"\nAttachments:\n{attachment_filenames}"

                await sync_to_async(send_mail)(
                    subject="New Message Notification",
                    message=email_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=True,
                )

            await self.send_json({"message": "Message sent successfully", "data": response_data})

        except Exception as e:
            print(f"Error in handle_send_message: {e}")
            await self.send_json({"error": f"An error occurred: {str(e)}"})

    async def chat_message(self, event):
        message = event["message"]
        await self.send_json({
            "action": "new_message",
            "data": message,
        })

    @staticmethod
    @sync_to_async
    def validate_user(model_class, token, email, token_optional=False):
        if token_optional or token:
            try:
                if hasattr(model_class, "email"):
                    return model_class.objects.get(email=email)
                else:
                    return model_class.objects.get(official_email=email)
            except model_class.DoesNotExist:
                raise ObjectDoesNotExist("User not found")
        raise ObjectDoesNotExist("Invalid email or token")

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.email = self.scope['url_route']['kwargs']['email']  # Fix variable name
#         self.group_name = f"notifications_{self.email.replace('@', '_at_').replace('.', '_dot_')}"

#         # Join the group
#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name,
#         )

#         # User is online
#         await self.update_online_status(self.email, True)

#         await self.accept()

#     async def disconnect(self, close_code):
#         # User is offline
#         await self.update_online_status(self.email, False)

#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name,
#         )

#     async def send_notification(self, event):
#         message = event['message']
#         await self.send(text_data=json.dumps({"message": message}))

#     @sync_to_async
#     def update_online_status(self, email, status):
#         OnlineStatus.objects.update_or_create(
#             email=email,
#             defaults={"is_online": status, "last_seen": now()},
#         )


class NotificationMessageConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.recipient_email = self.scope['url_route']['kwargs']['email']
        self.group_name = f"notifications_{self.recipient_email.replace('@', '_at_').replace('.', '_dot_')}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        # User is online
        await self.update_online_status(self.recipient_email, True)

        await self.accept()

    async def disconnect(self, close_code):
        # User is offline
        await self.update_online_status(self.recipient_email, False)

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def send_notification(self, event):
        message = event['message']
        await self.send_json({"message": message})

    @sync_to_async
    def update_online_status(self, email, status):
        OnlineStatus.objects.update_or_create(
            email=email,
            defaults={"is_online": status, "last_seen": now()},
        )
    
