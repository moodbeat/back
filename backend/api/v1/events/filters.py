from django_filters import rest_framework as filters

from events.models import Entry, Event
from socials.models import Like


class EntryFilter(filters.FilterSet):

    category = filters.CharFilter(
        field_name='category__slug', lookup_expr='icontains'
    )
    liked = filters.BooleanFilter(method='filter_liked')

    def filter_liked(self, queryset, name, value):
        user = self.request.user
        if value:
            liked_entries = (
                Like.objects
                .filter(author=user, entry__isnull=False)
                .values_list('entry', flat=True)
            )
            return queryset.filter(id__in=liked_entries)
        return queryset

    class Meta:
        model = Entry
        fields = ['category', 'id', 'title', 'liked']


class EventFilter(filters.FilterSet):

    liked = filters.BooleanFilter(method='filter_liked')

    def filter_liked(self, queryset, name, value):
        user = self.request.user
        if value:
            liked_events = (
                Like.objects
                .filter(author=user, event__isnull=False)
                .values_list('event', flat=True)
            )
            return queryset.filter(id__in=liked_events)
        return queryset

    class Meta:
        model = Event
        fields = ['id', 'author', 'departments', 'employees', 'liked']
