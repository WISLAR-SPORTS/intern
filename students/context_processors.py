# students/context_processors.py

def notification_count(request):

    if not request.user.is_authenticated:
        return {
            "unread_notification_count": 0
        }

    try:
        student = request.user.student

        count = student.notifications.filter(
            is_read=False,
            is_deleted=False
        ).count()

    except AttributeError:
        count = 0

    return {
        "unread_notification_count": count
    }
