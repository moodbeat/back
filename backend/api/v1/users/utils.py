import base64
import hashlib
from email.utils import formataddr

from django.conf import settings
from drf_yasg import openapi
from rest_framework.exceptions import ValidationError

from .tasks import send_mail_via_celery


def encode_data(secret_key: str, data: str) -> str:
    secret_key_hash = hashlib.sha256(secret_key.encode()).digest()
    return base64.b64encode(data.encode() + secret_key_hash).decode()


def decode_data(secret_key: str, encoded_data: str) -> str:
    secret_key_hash = hashlib.sha256(secret_key.encode()).digest()
    decoded_data = base64.b64decode(encoded_data)

    if decoded_data[-len(secret_key_hash):] != secret_key_hash:
        raise ValueError('Неверная пара ключ-значение')

    return decoded_data[:-len(secret_key_hash)].decode()

# ----------------------------------------------------------------
# Позже на рефакторинг, классом и с html шаблоном для письма


def send_invite_code(email: str, code: str, again: bool = False):
    subject = 'Ваша ссылка для прохождения регистрации'
    url = f'https://carefor-emp-mood.netlify.app/register?invite_code={code}'
    welcome = 'Регистрация на нашем сервисе.'

    if again:
        welcome = 'Вам отправлена повторная ссылка для регистрации.'

    message = (f'{welcome} \n\n'
               f'Для дальнейшей регистрации пройдите по адресу: {url}')
    recipient_list = [email]

    send_mail_via_celery.delay(
        subject,
        message,
        formataddr(('MoodBeat', settings.EMAIL_HOST_USER)),
        recipient_list,
        fail_silently=False,
    )


def send_reset_code(email: str, code: str, again: bool = False):
    subject = 'Сброс пароля'
    url = (
        'https://carefor-emp-mood.netlify.app/password-reset'
        f'?reset_code={code}'
    )
    welcome = 'Ваша ссылка для смены пароля.'

    if again:
        welcome = 'Вам отправлена повторная ссылка на смену пароля.'

    message = (f'{welcome} \n\n'
               f'Для смены пароля пройдите по адресу: {url}')
    recipient_list = [email]

    send_mail_via_celery.delay(
        subject,
        message,
        formataddr(('MoodBeat', settings.EMAIL_HOST_USER)),
        recipient_list,
        fail_silently=False,
    )
# ----------------------------------------------------------------


def verify_code(secret_key: str, code: str, obj: object) -> str:
    try:
        decode = decode_data(secret_key, code)
        obj.objects.get(code=decode)
        return decode
    except Exception:
        raise ValidationError({'detail': 'Недействительный ключ-приглашение'})


invite_code_param = openapi.Parameter(
    'invite_code',
    openapi.IN_QUERY,
    description=(
        'Неавторизованным пользователям необходимо предоставить '
        'действующий ключ-приглашение'
    ),
    type=openapi.TYPE_STRING
)
