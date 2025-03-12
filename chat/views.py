from django.http import JsonResponse # type: ignore
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.response import Response # type: ignore
from django.db.models import Q # type: ignore
from login.models import JobSeeker, new_user, CompanyInCharge, UniversityInCharge
from .models import Message
from rest_framework.permissions import AllowAny # type: ignore
from django.core.exceptions import ObjectDoesNotExist # type: ignore
from django.db.models import Max # type: ignore

MODEL_MAPPING = {
    "JobSeeker": JobSeeker,
    "UniversityInCharge": UniversityInCharge,
    "CompanyInCharge": CompanyInCharge,
    "new_user": new_user,
}


@api_view(['GET'])
def search_user(request):
    query = request.query_params.get("q", "").strip()
    if not query:
        return JsonResponse({"error": "Search query cannot be empty"}, status=400)

    result = []

    search_configs = {
        "User": {
            "fields": ["username"],
            "name_format": lambda instance: f"{getattr(instance, 'first_name', '')} {getattr(instance, 'last_name', '')}".strip()
        },
        "JobSeeker": {
            "fields": ["first_name", "last_name", "email"],
            "name_format": lambda instance: f"{instance.first_name} {instance.last_name}".strip()
        },
        "UniversityInCharge": {
            "fields": ["university_name", "official_email"],
            "name_format": lambda instance: instance.university_name
        },
        "CompanyInCharge": {
            "fields": ["company_name", "company_person_name", "official_email"],
            "name_format": lambda instance: instance.company_name
        },
        "new_user": {
            "fields": ["firstname", "lastname", "email"],
            "name_format": lambda instance: f"{instance.firstname} {instance.lastname}".strip()
        },
    }

    for model_name, config in search_configs.items():
        model_class = MODEL_MAPPING.get(model_name)
        if not model_class:
            continue

        query_filter = Q()
        for field in config["fields"]:
            query_filter |= Q(**{f"{field}__icontains": query})

        try:
            queryset = model_class.objects.filter(query_filter)
            for instance in queryset:
                user_data = {
                    "id": instance.id,
                    "model": model_name,
                    "email": getattr(instance, 'email', getattr(instance, 'official_email', None)),
                    "name": config["name_format"](instance),
                }
                result.append(user_data)
        except Exception as e:
            # print(f"Error fetching inbox: {str(e)}")
             return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return Response(result)

@api_view(['GET'])
@permission_classes([AllowAny])
def inbox(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Authorization header is missing or invalid'}, status=400)

    token = auth_header.split(' ')[1]

    user_model = request.query_params.get("user_model")
    user_email = request.query_params.get("user_email")
    message_type = request.query_params.get("message_type", "all")

    if not user_model or user_model not in MODEL_MAPPING:
        return JsonResponse({"error": "Invalid or missing user_model"}, status=400)
    if not user_email:
        return JsonResponse({"error": "user_email is required"}, status=400)

    user_model_class = MODEL_MAPPING[user_model]

    try:
        filter_params = {"email": user_email} if hasattr(user_model_class, "email") else {"official_email": user_email}
        user_model_class.objects.filter(token=token).get(**filter_params)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Invalid token or user not found'}, status=401)

    try:
        latest_messages = (
            Message.objects.filter(Q(sender_email=user_email) | Q(recipient_email=user_email))
            .values('sender_email', 'recipient_email')
            .annotate(latest_message_id=Max('id'))
        )

        latest_message_ids = [entry['latest_message_id'] for entry in latest_messages]

        messages = Message.objects.filter(id__in=latest_message_ids).order_by('-timestamp')
        if message_type == "read":
            messages = messages.filter(is_read=True)
        elif message_type == "unread":
            messages = messages.filter(is_read=False)

        inbox_data = []
        seen_conversations = set()

        for message in messages:
            conversation_with = (
                message.recipient_email if message.sender_email == user_email else message.sender_email
            )
            conversation_model = (
                message.recipient_model if message.sender_email == user_email else message.sender_model
            )

            if conversation_with in seen_conversations:
                continue

            seen_conversations.add(conversation_with)
            
            attachments = [
                {
                    "id": attachment.id,
                    "original_name": attachment.original_name,
                    "file_type": attachment.file_type,
                    "file_url": attachment.file_url
                }
                for attachment in message.attachments.all()
            ]

            inbox_data.append({
                "conversation_with": conversation_with,
                "conversation_model": conversation_model,
                "subject": message.subject,
                "latest_message": message.content,
                "timestamp": message.timestamp,
                "attachments": attachments,
            })

        return JsonResponse({
            "message": "Inbox retrieved successfully",
            "data": inbox_data
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

