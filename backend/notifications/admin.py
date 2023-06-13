from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('incident_type', 'user', 'is_viewed', 'creation_date',)
    list_filter = ('is_viewed', 'creation_date',)
    search_fields = ('user__first_name', 'user__last_name',)

    fieldsets = (
        (None, {
            'fields': ('incident_type', 'user', 'is_viewed',)
        }),
        ('Служебная информация', {
            'fields': ('creation_date',),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user',)
