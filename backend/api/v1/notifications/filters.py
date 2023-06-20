from django_filters import rest_framework as filters

from notifications.models import Notification


class NotificationFilter(filters.FilterSet):
    after_date = filters.DateFilter(method='filter_after_date')
    before_date = filters.DateFilter(method='filter_before_date')
    all_users = filters.BooleanFilter(
        method='filter_all_users'
    )

    class Meta:
        model = Notification
        fields = (
            'user', 'incident_type', 'incident_id', 'is_viewed',
        )

    def filter_after_date(self, queryset, name, value):
        return queryset.filter(creation_date__gte=value)

    def filter_before_date(self, queryset, name, value):
        return queryset.filter(creation_date__lte=value)

    def filter_all_users(self, queryset, name, value):
        if value and (
            self.request.user.is_authenticated
            and self.request.user.is_staff
        ):
            return self.Meta.model.objects.select_related('user').all()
        return queryset
