from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

from .models import Department, Hobby, InviteCode, Position

User = get_user_model()


class EmployeesCountMixin:
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(employees_count=Count('employees'))

    def employees_count(self, obj):
        return obj.employees_count

    employees_count.short_description = 'Сотрудников'


class UserInline(admin.TabularInline):
    model = User
    fields = ('last_name', 'first_name', 'email', 'phone')
    readonly_fields = ('last_name', 'first_name', 'email', 'phone')
    show_change_link = True
    show_full_result_count = True
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Department)
class DepartmentAdmin(EmployeesCountMixin, admin.ModelAdmin):
    list_display = ('name', 'employees_count')


@admin.register(Position)
class PositionAdmin(EmployeesCountMixin, admin.ModelAdmin):
    list_display = ('name', 'employees_count', 'chief_position')
    inlines = [UserInline, ]


@admin.register(Hobby)
class HobbyAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': (
            'email', 'first_name', 'last_name', 'patronymic', 'password'
        )}),
        (('Служебная информация'), {'fields': (
            'department', 'position', 'role', 'phone'
        )}),
        (('Прочее'), {'fields': ('avatar', 'hobbies')}),
        (('Роли и права'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (('Даты'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name',
                       'password1', 'password2'
                       ),
        }),
    )
    list_display = ('email', 'first_name', 'last_name',
                    'role', 'position')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('position', 'department')

    def save_model(self, request, obj, form, change):
        department = obj.department
        position = obj.position

        if department and position:
            if not position.departments.filter(pk=department.pk).exists():
                raise ValueError(
                    'Выбранная должность не принадлежит к указанному отделу.')

        super().save_model(request, obj, form, change)


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'sender', 'created', 'expire_date')
    readonly_fields = ('email', 'sender', 'created', 'expire_date')
    exclude = ('code',)
    ordering = ('-created',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
