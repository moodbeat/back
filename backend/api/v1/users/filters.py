import re

from django.conf import settings
from django_elasticsearch_dsl_drf import filter_backends
from elasticsearch_dsl.query import Match, Prefix, Wildcard
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.filters import BaseFilterBackend

from conf.service import invite_service
from users.models import InviteCode


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
            invite_service.verify_code(
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
        search_text = request.query_params.get('search', '').lower()
        search_text = re.sub(r'\d+', '', search_text)

        if search_text:
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

            query = match_name_query | prefix_name_query | wildcard_name_query
            search = view.search_document.search().query(query)
            return search.execute()

        return queryset
