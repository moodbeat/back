from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Condition, Survey, Question, Result, Variant


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ('user', 'mood', 'note', 'date')
    list_filter = ('mood', 'date')
    search_fields = ('user__first_name', 'user__last_name')
    ordering = ('user__email',)
    readonly_fields = ('date',)

    fieldsets = (
        (None, {
            'fields': ('user', 'mood', 'note')
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
