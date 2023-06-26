from django_filters import rest_framework as filters

from events.models import Entry, Event


class EntryFilter(filters.FilterSet):

    category = filters.CharFilter(
        field_name='category__slug', lookup_expr='icontains'
    )
    liked = filters.BooleanFilter(method='filter_liked')

    def filter_liked(self, queryset, name, value):
        if value:
            return queryset.filter(likes__employee=self.request.user)
        return queryset

    class Meta:
        model = Entry
        fields = ['category', 'id', 'title', 'liked']


class EventFilter(filters.FilterSet):

    liked = filters.BooleanFilter(method='filter_liked')

    def filter_liked(self, queryset, name, value):
        if value:
            return queryset.filter(likes__employee=self.request.user)
        return queryset

    class Meta:
        model = Event
        fields = ['id', 'author', 'departments', 'employees', 'liked']
