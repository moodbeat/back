from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Condition, Survey, Question, Result, Variant, \
    CompletedSurvey


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'mood', 'note', 'date')
    list_filter = ('mood', 'date')
    search_fields = ('employee__first_name', 'employee__last_name')
    ordering = ('employee__email',)
    readonly_fields = ('date',)

    fieldsets = (
        (None, {
            'fields': ('employee', 'mood', 'note')
        }),
        ('Служебная информация', {
            'fields': ('date',),
            'classes': ('collapse',)
        })
    )


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'department',
        'title',
        'description',
        'creation_date',
        'is_active',
    )
    list_filter = ('author', 'department', 'title')
    search_fields = (
        'title',
        'description',
        'author__first_name',
        'author__last_name'
    )
    ordering = ('-creation_date', 'title')
    readonly_fields = ('creation_date',)

    fieldsets = (
        (None, {
            'fields': ('author', 'department', 'title', 'description')
        }),
        ('Служебная информация', {
            'fields': ('creation_date', 'is_active'),
            'classes': ('collapse',)
        })
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('survey', 'text', 'priority',)
    list_filter = ('survey', 'text', 'priority',)
    search_fields = ('survey', 'text')
    ordering = ('id',)

    fieldsets = (
        (None, {
            'fields': ('survey', 'text',)
        }),
        ('Служебная информация', {
            'fields': ('priority',),
            'classes': ('collapse',)
        })
    )


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('survey', 'description', 'level',)
    list_filter = ('survey', 'description', 'level',)
    search_fields = ('survey', 'description')
    ordering = ('id',)


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('question', 'text',)
    list_filter = ('question', 'text',)
    search_fields = ('question', 'text',)
    ordering = ('id',)


@admin.register(CompletedSurvey)
class CompletedSurvey(admin.ModelAdmin):
    list_display = ('employee', 'survey', 'result', 'completion_date')
    list_filter = ('completion_date', 'employee', 'survey')
    search_fields = ('employee', 'survey')
    ordering = ('completion_date', 'employee')
