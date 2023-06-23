from datetime import date, timedelta

from celery import shared_task
from django.db.models import Q

from .models import Notification


@shared_task(name='del_old_viewed_notifications')
def delete_old_viwed_notifications(days):
    date_earlier = date.today() - timedelta(days=int(days))
    Notification.objects.filter(
        Q(creation_date__lte=date_earlier)
        & Q(is_viewed=True)
    ).delete()
