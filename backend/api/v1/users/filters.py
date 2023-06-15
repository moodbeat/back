from django.conf import settings
from django_elasticsearch_dsl_drf import filter_backends
from elasticsearch_dsl.query import Bool, Match, Prefix, Wildcard
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.filters import BaseFilterBackend

from users.models import InviteCode

from .utils import verify_code


class InviteCodeFilter(BaseFilterBackend):
    """Доступ для гостей только по ключу-приглашению."""

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
    """При выборе должностей исключать руководящие."""

    def filter_queryset(self, request, queryset, view):
        queryset = super().filter_queryset(request, queryset, view)
        if not request.user.is_authenticated:
            return queryset.exclude(chief_position=True)
        return queryset


class DepartmentInviteCodeFilter(InviteCodeFilter):
    """
    Фильтр по отделам.

    Исключает отделы без должностей или только с руководящими должностями.

    """

    def filter_queryset(self, request, queryset, view):
        queryset = super().filter_queryset(request, queryset, view)
        if not request.user.is_authenticated:
            return queryset.filter(positions__chief_position=False).distinct()
        return queryset


class ElasticSearchFilter(filter_backends.BaseSearchFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_text = request.query_params.get('search', '')
        if search_text:
            search_document = view.search_document
            bool_query = Bool(should=[])

            match_name_query = Match(
                name={
                    'query': search_text,
                    'fuzziness': 'AUTO',
                    'prefix_length': 0,
                    'max_expansions': 10
                }
            )
            prefix_name_query = Prefix(name=search_text)
            wildcard_name_query = Wildcard(name=f'*{search_text}*')

            bool_query.should.extend([
                match_name_query,
                prefix_name_query,
                wildcard_name_query
            ])
            search = search_document.search().query(bool_query)
            return search.execute()

        return queryset
