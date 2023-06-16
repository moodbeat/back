from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver

from metrics.models import CompletedSurvey, Survey
from metrics.result_calcs import MBICalculate, YesNoCalculate
from notifications.models import Notification
from notifications.signals.handlers import notification

User = get_user_model()


@receiver(pre_save, sender=CompletedSurvey)
def calc_results_for_survey(sender, instance, **kwargs):

    survey_types = {
        'yn': YesNoCalculate,
        'mbi': MBICalculate
    }

    survey_type = instance.survey.type.slug

    if survey_type in survey_types:
        handler_class = survey_types[survey_type]
        handler = handler_class()
        handler.calculate_results(instance)

    if instance.survey.frequency:
        instance.next_attempt_date = date.today() + timedelta(
            days=instance.survey.frequency
        )


@receiver(m2m_changed, sender=Survey.department.through)
def create_notification_for_event_by_departments(
    action, pk_set, instance, **kwargs
):
    """Вызывается при cвязывании объекта модели `Survey` с `Department`.

    В результате в БД создаются объекты модели `Notification`
    для всех пользователей, связанных с департаментами - полем
    `departments`.
    """
    if action == 'post_add':
        results = Notification.objects.bulk_create([
            Notification(
                incident_type=Notification.IncidentType.SURVEY,
                incident_id=instance.id,
                user=obj
            ) for obj in User.objects.filter(
                Q(department__in=pk_set) & Q(is_active=True)
            )
        ])
        for obj in results:
            notification.send(sender=Notification, instance=obj)
