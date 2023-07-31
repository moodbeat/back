from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import (ActivityRate, ActivityTracker, ActivityType,
                     BurnoutTracker, CompletedSurvey, Condition, LifeDirection,
                     Question, Survey, SurveyType, UserLifeBalance, Variant)


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


@admin.register(BurnoutTracker)
class BurnoutTrackerAdmin(admin.ModelAdmin):
    list_display = ('date', 'employee', 'mental_state')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


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
        'creation_date',
        'for_all',
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
            'fields': ('author', 'title', 'type', 'for_all', 'department',
                       'description', 'text', 'frequency', 'min_range',
                       'max_range')
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

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'description',)
    ordering = ('key',)


class ActivityRateFormSet(BaseInlineFormSet):

    # https://stackoverflow.com/questions/4735920/
    def clean(self):
        super(ActivityRateFormSet, self).clean()

        percent = 0
        activity_types = set()

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            data = form.cleaned_data
            percent += data.get('percentage', 0)

            activity_type = data.get('type')
            if activity_type in activity_types:
                raise ValidationError('Элементы должны быть уникальными.')
            activity_types.add(activity_type)

        if percent != 100:
            raise ValidationError('Суммарный процент должен быть равен 100%.')


class ActivityRateInline(admin.TabularInline):
    model = ActivityRate
    formset = ActivityRateFormSet
    extra = 0
    can_delete = False


@admin.register(ActivityTracker)
class ActivityTrackerAdmin(admin.ModelAdmin):
    list_display = ('date', 'employee',)
    ordering = ('-date',)
    inlines = [ActivityRateInline]
