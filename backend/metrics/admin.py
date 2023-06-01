from django.contrib import admin

from .models import (CompletedSurvey, Condition, Question, Survey,
                     SurveyDepartment)


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'mood', 'note', 'date')
    list_filter = ('mood', 'date')
    search_fields = ('employee__first_name', 'employee__last_name')
    ordering = ('-date',)

    fieldsets = (
        (None, {
            'fields': ('employee', 'mood', 'note')
        }),
        ('Служебная информация', {
            'fields': ('date',),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('employee',)


class SurveyDepartmentInline(admin.TabularInline):
    model = SurveyDepartment


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'title',
        'description',
        'creation_date',
        'is_active',
    )
    list_filter = ('department',)
    search_fields = (
        'title',
        'description',
        'author__first_name',
        'author__last_name'
    )
    inlines = (SurveyDepartmentInline,)
    ordering = ('-creation_date', 'title')
    readonly_fields = ('creation_date',)

    fieldsets = (
        (None, {
            'fields': ('author', 'title', 'description', 'frequency')
        }),
        ('Служебная информация', {
            'fields': ('creation_date', 'is_active',),
            'classes': ('collapse',)
        })
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('survey', 'text',)
    list_filter = ('survey',)
    search_fields = ('survey', 'text',)
    ordering = ('id',)

    fieldsets = (
        (None, {
            'fields': ('survey', 'text',)
        }),
    )


@admin.register(CompletedSurvey)
class CompletedSurvey(admin.ModelAdmin):
    list_display = ('employee', 'survey', 'result', 'completion_date',)
    list_filter = ('completion_date', 'survey', 'result',)
    search_fields = ('employee', 'survey',)
    ordering = ('-completion_date', 'employee', 'survey',)

    fieldsets = (
        (None, {
            'fields': (
                'employee', 'survey', 'positive_value',
                'negative_value', 'completion_date',
            )
        }),
        ('Служебная информация', {
            'fields': ('next_attempt_date',),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('employee', 'survey')
