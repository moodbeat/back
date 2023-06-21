from datetime import date

from celery import shared_task

from notifications.models import Notification

from .models import CompletedSurvey


@shared_task(name='send_survey_notifications')
def send_everyday_survey_notifications():
    Notification.objects.bulk_create([
        Notification(
            incident_type=Notification.IncidentType.SURVEY,
            incident_id=obj.survey.id,
            user=obj.employee
        ) for obj in CompletedSurvey.objects.filter(
            next_attempt_date=date.today()
        )
    ])
