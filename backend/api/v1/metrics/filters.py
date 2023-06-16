from datetime import date

from django_filters import rest_framework as filters

from metrics.models import CompletedSurvey, Condition, Survey


class ConditionFilter(filters.FilterSet):
    position = filters.CharFilter(
        field_name='employee__position', lookup_expr='exact'
    )
    department = filters.CharFilter(
        field_name='employee__department', lookup_expr='exact'
    )
    my_conditions = filters.BooleanFilter(method='filter_my_conditions')

    class Meta:
        model = Condition
        fields = ('employee', 'position', 'department')

    def filter_my_conditions(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(employee=self.request.user)
        return queryset


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
    my_results = filters.BooleanFilter(method='filter_my_results')

    class Meta:
        model = CompletedSurvey
        fields = ('employee', 'survey', 'completion_date')

    def filter_my_results(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(employee=self.request.user)
        return queryset
