from django.urls import include, path, re_path

from api.v1.utils import OptionalSlashRouter

from . import views

v10 = OptionalSlashRouter()
v10.register('users', views.UserViewSet, basename='users')
v10.register('hobbies', views.HobbyViewSet, basename='hobbies')
v10.register('departments', views.DepartmentViewSet, basename='departments')
v10.register('positions', views.PositionViewSet, basename='positions')

urlpatterns = [
    re_path(
        r'^users/current_user/?$',
        views.CurrentUserView.as_view(),
        name='current_user'
    ),
    re_path(
        r'^users/send_invite/?$',
        views.SendInviteView.as_view(),
        name='send_invite'
    ),
    re_path(
        r'^users/register/?$',
        views.RegisterView.as_view(),
        name='register'
    ),
    re_path(
        r'^users/verify_invite/?$',
        views.VerifyInviteView.as_view(),
        name='verify_invite'
    ),
    re_path(
        r'^users/password_reset/?$',
        views.PasswordResetView.as_view(),
        name='password_reset'
    ),
    re_path(
        r'^users/password_reset_confirm/?$',
        views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    re_path(
        r'^users/password_change/?$',
        views.PasswordChangeView.as_view(),
        name='password_change'
    ),
    re_path(
        r'^users/send_telegram_code/?$',
        views.TelegramSendCodeView.as_view(),
        name='send_telegram_code'
    ),
    path('', include(v10.urls)),
]
