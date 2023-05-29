from datetime import date

from django_filters import rest_framework as filters

from metrics.models import CompletedSurvey, Survey


class SurveyFilter(filters.FilterSet):

    class Meta:
        model = Survey
        fields = ('author', 'department', 'is_active')

    @property
    def qs(self):
        parent = super().qs
        exc_surey = Survey.objects.filter(
            completedsurvey__employee=self.request.user,
            completedsurvey__next_attempt_date__gt=date.today(),
        ).values('id')
        return parent.exclude(id__in=(exc_surey))


class CompletedSurveyFilter(filters.FilterSet):

    class Meta:
        model = CompletedSurvey
        fields = ('employee', 'survey', 'completion_date', 'result')
