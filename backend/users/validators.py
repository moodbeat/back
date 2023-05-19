import re

from django.core.exceptions import ValidationError


class UppercasePasswordValidator:
    message = ('Пароль должен содержать хотя бы %(min_count)d '
               'букв%(plural)s верхнего регистра.')
    pattern = '[A-ZА-Я]'
    code = 'password_no_upper'

    def __init__(self, min_count=1):
        self.min_count = min_count

    def validate(self, password, user=None):
        word_count = len(re.findall(self.pattern, password))
        if word_count < self.min_count:
            params = {
                'min_count': self.min_count,
                'plural': 'ы' if self.min_count > 1 else 'у'
            }
            raise ValidationError(
                self.message,
                code=self.code,
                params=params
            )

    def get_help_text(self):
        return (
            self.message % {
                'min_count': self.min_count,
                'plural': 'ы' if self.min_count > 1 else 'у'
            })


class LowercasePasswordValidator(UppercasePasswordValidator):
    message = ('Пароль должен содержать хотя бы %(min_count)d '
               'букв%(plural)s нижнего регистра.')
    pattern = '[a-zа-я]'
    code = 'password_no_lower'


class NoSpacesPasswordValidator:
    message = 'Пароль не должен содержать пробелов.'

    def validate(self, password, user=None):
        if ' ' in password:
            raise ValidationError(
                self.message,
                code='password_has_spaces'
            )

    def get_help_text(self):
        return self.message


class MaximumLengthPasswordValidator:
    message = ('Пароль не должен содержать больше %(max_length)d символов')
    code = 'password_max_length'

    def __init__(self, max_length=254):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            params = {'max_length': self.max_length}
            raise ValidationError(
                self.message,
                code=self.code,
                params=params
            )

    def get_help_text(self):
        return (self.message % {'max_length': self.max_length})


def validate_name(value, name: str, plural: str, plural2: str):
    if len(value) < 2:
        raise ValidationError(
            f'{name} должн{plural} содержать минимум 2 символа'
        )
    if not re.match(r'^[а-яА-Я]+(-[а-яА-Я]+)?$', value):
        raise ValidationError(f'Некорректн{plural2} {name.lower()}')


def validate_first_name(value):
    validate_name(value, 'Имя', 'о', 'ое')


def validate_last_name(value):
    validate_name(value, 'Фамилия', 'а', 'ая')


def validate_patronymic(value):
    validate_name(value, 'Отчество', 'о', 'ое')
