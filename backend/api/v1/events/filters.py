from django_filters import rest_framework as filters

from events.models import Entry


class EntryFilter(filters.FilterSet):
    category = filters.CharFilter(
        field_name='category__slug', lookup_expr='icontains'
    )

    class Meta:
        model = Entry
        fields = ['category', 'id', 'title']
