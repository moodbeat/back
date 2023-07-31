import base64
import hashlib
from email.utils import formataddr

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from drf_yasg import openapi
from rest_framework.exceptions import ValidationError

from .tasks import send_mail_via_celery, send_mass_mail_via_celery


class EmailService:
    def send_email(
        self,
        subject,
        message,
        from_email,
        recipient_list,
        html_message=None
    ):
        """Отправка email-сообщения пользователю."""
        send_mail_via_celery.delay(
            subject,
            message,
            from_email,
            recipient_list,
            html_message=html_message,
        )

    def send_mass_email(
        self,
        datatuple
    ):
        """Отправка нескольких email-сообщений за раз."""
        send_mass_mail_via_celery(
            datatuple
        )


class SecretCodeService:
    def decode_data(self, secret_key: str, encoded_data: str):
        """Декодирует данные по секретному ключу."""
        secret_key_hash = hashlib.sha256(secret_key.encode()).digest()
        decoded_data = base64.b64decode(encoded_data)

        if decoded_data[-len(secret_key_hash):] != secret_key_hash:
            raise ValueError('Неверная пара ключ-значение')

        return decoded_data[:-len(secret_key_hash)].decode()

    def encode_data(self, secret_key: str, data: str):
        """Кодирует данные по секретному ключу."""
        secret_key_hash = hashlib.sha256(secret_key.encode()).digest()
        return base64.b64encode(data.encode() + secret_key_hash).decode()


class InviteService(SecretCodeService, EmailService):
    host = settings.SELF_HOST
    invite_code_param = openapi.Parameter(
        'invite_code',
        openapi.IN_QUERY,
        description=(
            'Неавторизованным пользователям необходимо предоставить '
            'действующий ключ-приглашение'
        ),
        type=openapi.TYPE_STRING
    )

    def verify_code(self, secret_key: str, code: str, obj: object):
        """Проверяет ключ-приглашение на соответствие."""
        try:
            decode = self.decode_data(secret_key, code)
            obj.objects.get(code=decode)
            return decode
        except Exception:
            raise ValidationError(
                {'detail': 'Недействительный ключ-приглашение'}
            )

    def send_invite_code(self, email: str, code: str, again: bool = False):
        """Отправляет `email` c ссылкой для регистрации пользователя."""
        url = f'{self.host}register?invite_code={code}'
        subject = 'Регистрация на нашем сервисе'
        if again:
            subject = 'Вам отправлена повторная ссылка для регистрации'
        html_message = render_to_string(
            'email/send_invitation_link.html',
            {'url': url},
        )
        message = strip_tags(html_message)

        self.send_email(
            subject,
            message,
            formataddr(('MoodBeat', settings.EMAIL_HOST_USER)),
            [email],
            html_message=html_message,
        )

    def send_reset_code(self, email: str, code: str, again: bool = False):
        """Отправляет `email` c ссылкой для смены пароля пользователя."""
        url = (
            f'{self.host}password-reset?reset_code={code}'
        )
        subject = 'Ваша ссылка для смены пароля'
        if again:
            subject = 'Вам отправлена повторная ссылка на смену пароля'
        html_message = render_to_string(
            'email/send_password_restore_email.html',
            {'url': url},
        )
        message = strip_tags(html_message)

        self.send_email(
            subject,
            message,
            formataddr(('MoodBeat', settings.EMAIL_HOST_USER)),
            [email],
            html_message=html_message,
        )

    def send_telegram_code(self, email: str, code: str, again: bool = False):
        """Отправляет `email` c кодом для авторизации в боте."""
        url = (
            f'https://t.me/{settings.BOT_NAME}'
        )
        subject = 'Ваш код для авторизации в боте'
        if again:
            subject = 'Вам повторно отправлен код для авторизации в боте'
        html_message = render_to_string(
            'email/send_telegram_code.html',
            {'url': url, 'code': code},
        )
        message = strip_tags(html_message)

        self.send_email(
            subject,
            message,
            formataddr(('MoodBeat', settings.EMAIL_HOST_USER)),
            [email],
            html_message=html_message,
        )


class NotificationEmailService(EmailService):
    host = settings.SELF_HOST

    def send_notification_on_email(self, user, incident_type):
        """Отправляет пользователю `email` напоминание о новых событиях."""
        url = self.host
        subject = 'Новые уведомления'
        html_message = render_to_string(
            'email/send_new_notifications.html',
            {'incident_type': incident_type, 'url': url},
        )
        message = strip_tags(html_message)

        self.send_email(
            subject,
            message,
            formataddr(('MoodBeat', settings.EMAIL_HOST_USER)),
            [user.email],
            html_message=html_message,
        )


class ContactMessageEmailService(EmailService):
    contact_email = settings.CONTACT_EMAIL

    def send_contact_message_on_email(self, name, email, comment):
        """Отправляет пользователю `email` с сообщением из контактной формы."""
        contact_email = self.contact_email
        subject = 'Обратная связь'
        html_message = render_to_string(
            'email/send_contact_form.html',
            {'name': name, 'email': email, 'comment': comment},
        )
        message = strip_tags(html_message)

        self.send_email(
            subject,
            message,
            formataddr(('MoodBeat', settings.EMAIL_HOST_USER)),
            [contact_email],
            html_message=html_message,
        )


contact_message_service = ContactMessageEmailService()
invite_service = InviteService()
notification_email_service = NotificationEmailService()
