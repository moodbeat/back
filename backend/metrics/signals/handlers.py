from datetime import date, timedelta

from django.db.models.signals import pre_save
from django.dispatch import receiver

from metrics.models import CompletedSurvey
from metrics.result_calcs import MBICalculate, YesNoCalculate


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
