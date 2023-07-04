from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.signals import (m2m_changed, post_delete, post_save,
                                      pre_save)
from django.dispatch import receiver

from metrics.models import BurnoutTracker, CompletedSurvey, Survey
from metrics.result_calcs import MBICalculate, YesNoCalculate
from notifications.models import Notification

User = get_user_model()


@receiver(pre_save, sender=CompletedSurvey)
def calc_results_for_survey(sender, instance, **kwargs):
    """Вызывается перед сохранением объекта `CompletedSurvey`.

    Производится расчет результатов в зависимости от типа пройденого опроса
    и назначается время когда опрос можно пройти в следующий раз.
    """
    survey_types = {
        'yn': YesNoCalculate,
        'mbi': MBICalculate
    }

    survey_type = instance.survey.type.slug

    if survey_type in survey_types:
        handler_class = survey_types[survey_type]
        handler = handler_class(instance)
        handler.calculate()

    if instance.survey.frequency:
        instance.next_attempt_date = date.today() + timedelta(
            days=instance.survey.frequency
        )


@receiver(post_save, sender=CompletedSurvey)
def add_mental_state_to_tracker(sender, instance, created, **kwargs):
    """Вызывается после сохранения объекта `CompletedSurvey`.

    По итогам теста обновляет трекер выгорания.
    """
    if created:
        BurnoutTracker.objects.create(
            employee=instance.employee,
            mental_state=instance.mental_state,
            date=instance.completion_date
        )


@receiver(post_save, sender=Survey)
def create_notification_for_all(sender, instance, created, **kwargs):
    """Вызывается после сохранения объекта `Survey`.

    Идет проверка, что объект только что создан и проверяет положительно ли
    значение параметра for_all. При этих двух условиях создаются уведомления
    для всех активных пользователей сервиса.
    """
    if created and instance.for_all:
        Notification.objects.bulk_create([
            Notification(
                incident_type=Notification.IncidentType.SURVEY,
                incident_id=instance.id,
                user=obj
            ) for obj in User.objects.filter(is_active=True)
        ])


@receiver(post_delete, sender=Survey)
def delete_notifications_after_obj_delete(sender, instance, *args, **kwargs):
    """Вызывается после удаления объекта `Survey`.

    Удаляются все уведомления с id и типом удаленного экземпляра `Survey`.
    """
    Notification.objects.filter(
        incident_id=instance.id,
        incident_type=Notification.IncidentType.SURVEY
    ).delete()


@receiver(m2m_changed, sender=Survey.department.through)
def create_notification_by_departments(
    action, pk_set, instance, **kwargs
):
    """Вызывается при cвязывании объекта модели `Survey` с `Department`.

    В результате в БД создаются объекты модели `Notification`
    для всех пользователей, связанных с департаментами - полем
    `departments`.
    """
    if action == 'post_add' and instance.for_all is False:
        Notification.objects.bulk_create([
            Notification(
                incident_type=Notification.IncidentType.SURVEY,
                incident_id=instance.id,
                user=obj
            ) for obj in User.objects.filter(
                Q(department__in=pk_set) & Q(is_active=True)
            )
        ])
