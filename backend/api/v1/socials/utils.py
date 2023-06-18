from drf_yasg import openapi

user_param = openapi.Parameter(
    'user',
    openapi.IN_QUERY,
    description=(
        'Фильтр типов помощи по пользователям, которые могут её оказать.'
    ),
    type=openapi.TYPE_STRING
)
