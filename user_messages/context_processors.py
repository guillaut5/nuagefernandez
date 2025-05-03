from .models import MessageReadStatus


def new_messages_count(request):
    if request.user.is_authenticated:
        count = MessageReadStatus.objects.filter(
            user=request.user, is_read=False, is_deleted=False
        ).count()
    else:
        count = 0
    return {"new_messages_count": count}
