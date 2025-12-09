from django.template import Library
from ..models import Notification

register = Library()

@register.simple_tag(takes_context=True)
def unread_notifications_count(context):
    request = context.get('request')
    if request and request.user.is_authenticated:
        return Notification.objects.filter(user=request.user, is_read=False).count()
    return 0
