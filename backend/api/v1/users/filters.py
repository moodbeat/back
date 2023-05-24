from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.filters import BaseFilterBackend
from users.models import InviteCode

from .utils import verify_code


class InviteCodeFilter(BaseFilterBackend):
    '''Доступ для гостей только по ключу-приглашению'''

    def filter_queryset(self, request, queryset, view):
        invite_code = request.query_params.get('invite_code')

        if not request.user.is_authenticated and not invite_code:
            raise AuthenticationFailed(
                'Неавторизованным пользователям необходимо предоставить '
                'действующий ключ-приглашение'
            )
        if invite_code is not None:
            verify_code(
                settings.RESET_INVITE_SECRET_KEY, invite_code, InviteCode
            )
        return queryset


class PositionInviteCodeFilter(InviteCodeFilter):
    '''При выборе должностей исключать руководящие'''

    def filter_queryset(self, request, queryset, view):
        queryset = super().filter_queryset(request, queryset, view)
        if not request.user.is_authenticated:
            return queryset.exclude(chief_position=True)
        return queryset


class DepartmentInviteCodeFilter(InviteCodeFilter):
    '''
    Фильтр по отделам, исключающий отделы без должностей или
    только с руководящими должностями
    '''

    def filter_queryset(self, request, queryset, view):
        queryset = super().filter_queryset(request, queryset, view)
        if not request.user.is_authenticated:
            return queryset.filter(positions__chief_position=False).distinct()
        return queryset
