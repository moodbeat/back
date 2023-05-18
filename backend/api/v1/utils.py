import base64
import hashlib

from django.core.mail import send_mail
from drf_yasg import openapi
from rest_framework.exceptions import ValidationError


def encode_data(secret_key: str, data: str) -> str:
    secret_key_hash = hashlib.sha256(secret_key.encode()).digest()
    encoded_data = base64.b64encode(data.encode() + secret_key_hash).decode()
    return encoded_data


def decode_data(secret_key: str, encoded_data: str) -> str:
    secret_key_hash = hashlib.sha256(secret_key.encode()).digest()
    decoded_data = base64.b64decode(encoded_data)

    if decoded_data[-len(secret_key_hash):] != secret_key_hash:
        raise ValueError('Неверная пара ключ-значение')

    return decoded_data[:-len(secret_key_hash)].decode()


def send_code(email: str, code: str, again: bool = False):
    subject = 'Приглашение на сайт'
    url = f'https://url/register?invite={code}'
    welcome = 'Добро пожаловать на наш сайт.'

    if again:
        welcome = 'Вам отправлена повторная ссылка для регистрации.'

    message = (f'{welcome} \n'
               f'Для дальнейшей регистрации пройдите по адресу: {url}')
    from_email = 'noreply@example.com'
    recipient_list = [email]

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )


def verify_code(secret_key: str, code: str) -> str:
    try:
        decode = decode_data(secret_key, code)
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
