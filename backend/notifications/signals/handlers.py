from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from events.models import Event
from metrics.models import SurveyDepartment

from ..models import Notification

User = get_user_model()


@receiver(m2m_changed, sender=Event.departments.through)
def create_notification_for_event_by_departments(
    action, pk_set, **kwargs
):
    """Вызывается при cвязывании объекта модели `Event` с `Department`.

    В результате в БД создаются объекты модели `Notification`
    для всех пользователей из поля `employees` модели `Event`
    и пользователей связанных с департаментами - полем
    `departments`.
    """
    print('heu')
    if action == 'post_add':
        Notification.objects.bulk_create([
            Notification(
                incident_type=Notification.IncidentType.EVENT,
                user=obj
            ) for obj in User.objects.filter(
                Q(department__in=pk_set) & Q(is_active=True)
            )
        ])


@receiver(m2m_changed, sender=Event.departments.through)
def create_notification_for_event_by_employees(
    action, pk_set, **kwargs
):
    """Вызывается при cвязывании объекта модели `Event` с `User`.

    В результате в БД создаются объекты модели `Notification`
    для всех пользователей из поля `employees` модели `Event`
    и пользователей связанных с департаментами - полем
    `departments`.
    """
    if action == 'post_add':
        Notification.objects.bulk_create([
            Notification(
                incident_type=Notification.IncidentType.EVENT,
                user=obj
            ) for obj in User.objects.filter(
                Q(id__in=pk_set) & Q(is_active=True)
            )
        ])


@receiver(post_save, sender=SurveyDepartment)
def create_notification_for_survey(sender, instance, created, **kwargs):
    """Вызывается при cвязывании объекта модели `Survey` с `Department`.

    В результате в БД создаются объекты модели `Notification`
    для всех пользователей из связанных департаментов модели `Survey`.
    """
    if created:
        Notification.objects.bulk_create([
            Notification(
                incident_type=Notification.IncidentType.SURVEY,
                user=obj
            ) for obj in User.objects.filter(
                Q(department=instance.id) & Q(is_active=True)
            )
        ])


@receiver(post_save, sender=Notification)
def get_data_for_websocket(sender, instance, **kwargs):
    """Вызывается при создании нового объекта модели `Notification`.

    Отправляются данные пользователю в вебсокет.
    """
    channel_layer = get_channel_layer()
    group_name = 'user_%s' % instance.user.id
    data = instance.user.notifications.filter(is_viewed=False).values(
        'incident_type'
    ).annotate(
        incident_count=Count('incident_type')
    )
    async_to_sync(channel_layer.group_send)(
        group_name, {"type": "notification", "data": list(data)}
    )


m2m_changed.connect(
    create_notification_for_event_by_departments,
    sender=Event.departments.through
)
m2m_changed.connect(
    create_notification_for_event_by_employees, sender=Event.employees.through
)
post_save.connect(create_notification_for_survey, sender=SurveyDepartment)
post_save.connect(get_data_for_websocket, sender=Notification)
