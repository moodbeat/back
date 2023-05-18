from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.filters import BaseFilterBackend

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

        verify_code(settings.INVITE_SECRET_KEY, invite_code)
        return queryset
