from django.contrib import admin

from .models import (CompletedSurvey, Condition, LifeDirection, Question,
                     Survey, SurveyType, UserLifeBalance, Variant)


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


@admin.register(LifeDirection)
class LifeDirectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'num',)
    readonly_fields = ('num',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if obj:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserLifeBalance)
class UserLifeBalanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'employee', 'set_priority')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class QuestionInlineAdmin(admin.TabularInline):
    model = Question
    fields = ('survey', 'text', 'key', 'priority')
    show_change_link = True
    show_full_result_count = True
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('survey', 'text', 'key', 'priority')
    list_filter = ('survey',)


@admin.action(description='Удалить вместе с вопросами')
def delete_survey_questions(modeladmin, request, queryset):
    Question.objects.filter(survey__in=queryset).delete()


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'title',
        'type',
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
    ordering = ('-creation_date', 'title')
    readonly_fields = ('creation_date',)
    inlines = (QuestionInlineAdmin,)
    list_display_links = ('title',)
    actions = (delete_survey_questions,)
    save_on_top = True

    fieldsets = (
        (None, {
            'fields': ('author', 'title', 'type', 'description', 'text',
                       'frequency', 'min_range', 'max_range')
        }),
        ('Служебная информация', {
            'fields': ('creation_date', 'is_active',),
            'classes': ('collapse',)
        })
    )


@admin.register(SurveyType)
class SurveyType(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    ordering = ('id',)


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey_type', 'priority', 'value')
    ordering = ('id',)


@admin.register(CompletedSurvey)
class CompletedSurvey(admin.ModelAdmin):
    list_display = ('employee', 'survey', 'mental_state', 'completion_date',)
    list_filter = ('survey',)
    search_fields = ('employee', 'survey',)
    ordering = ('-completion_date', 'employee', 'survey',)

    fieldsets = (
        (None, {
            'fields': (
                'employee', 'survey',
                'results', 'completion_date',
            )
        }),
        ('Служебная информация', {
            'fields': ('next_attempt_date',),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('employee', 'survey', 'mental_state')
