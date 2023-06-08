import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator)
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .managers import UserManager
from .validators import (alpha_space_dash_validator, validate_email_latin,
                         validate_email_prefix, validate_first_name,
                         validate_last_name, validate_patronymic)


class Department(models.Model):

    name = models.CharField(
        verbose_name='Наименование',
        unique=True,
        max_length=48,
        validators=[
            MinLengthValidator(2),
            alpha_space_dash_validator
        ]
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=254,
        null=True,
        blank=True,
        validators=[MinLengthValidator(8)]
    )

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'

    def __str__(self):
        return self.name


class Position(models.Model):

    name = models.CharField(
        verbose_name='Название должности',
        unique=True,
        max_length=48,
        validators=[
            MinLengthValidator(2),
            alpha_space_dash_validator
        ]
    )
    departments = models.ManyToManyField(
        Department,
        verbose_name='Отделы',
        related_name='positions',
        blank=True
    )
    chief_position = models.BooleanField(
        verbose_name='Руководящая должность',
        default=False
    )

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.name


class Hobby(models.Model):

    name = models.CharField(
        verbose_name='Наименование',
        max_length=32,
        unique=True,
        validators=[
            MinLengthValidator(2),
            alpha_space_dash_validator
        ]
    )

    class Meta:
        verbose_name = 'Интерес'
        verbose_name_plural = 'Интересы'

    def __str__(self):
        return self.name


class MentalState(models.Model):

    LEVELS = (
        (1, 'Норма'),
        (2, 'Плохо'),
        (3, 'Критический уровень')
    )

    name = models.CharField(
        verbose_name='Наименование',
        max_length=128,
        validators=[MinLengthValidator(2)]
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=512,
        blank=True,
        null=True
    )
    level = models.PositiveSmallIntegerField(
        verbose_name='Уровень',
        default=1,
        choices=LEVELS,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(3)
        ]
    )

    class Meta:
        verbose_name = 'Психологическое состояние'
        verbose_name_plural = 'Психологические состояния'

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):

    HR = 'hr'
    CHIEF = 'chief'
    EMPLOYEE = 'employee'

    ROLES = (
        (HR, 'HR'),
        (CHIEF, 'Руководитель'),
        (EMPLOYEE, 'Работник')
    )

    email = models.EmailField(
        verbose_name=_('email'),
        unique=True,
        max_length=254,
        validators=[
            MinLengthValidator(8),
            validate_email_latin,
            validate_email_prefix
        ]
    )
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=32,
        validators=[validate_first_name, MinLengthValidator(2)]
    )
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=32,
        validators=[validate_last_name, MinLengthValidator(2)]
    )
    patronymic = models.CharField(
        verbose_name='Отчество',
        max_length=32,
        blank=True,
        null=True,
        validators=[validate_patronymic, MinLengthValidator(2)]
    )
    department = models.ForeignKey(
        Department,
        verbose_name='Отдел',
        related_name='employees',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    position = models.ForeignKey(
        Position,
        verbose_name='Должность',
        related_name='employees',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    mental_state = models.ForeignKey(
        MentalState,
        verbose_name='Психологическое состояние',
        related_name='employees',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    hobbies = models.ManyToManyField(
        Hobby,
        verbose_name='Хобби',
        related_name='users',
        blank=True
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=ROLES,
        max_length=10,
        default='employee',
        db_index=True
    )
    avatar_full = models.ImageField(
        verbose_name='Аватар/Фото',
        upload_to='users/avatars/',
        blank=True,
        null=True
    )
    about = models.TextField(
        verbose_name='О себе',
        max_length=256,
        blank=True,
        null=True,
        validators=[MinLengthValidator(2)]
    )
    phone = PhoneNumberField(
        verbose_name='Телефон',
        max_length=12,
        blank=True,
        null=True
    )
    is_staff = models.BooleanField(
        verbose_name=_('staff status'),
        default=False
    )
    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True
    )
    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        default=timezone.now,
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def is_hr(self):
        return self.role == self.HR

    @property
    def is_chief(self):
        return self.role == self.CHIEF

    @property
    def is_employee(self):
        return self.role == self.EMPLOYEE

    @property
    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
        constraints = [
            UniqueConstraint(
                Lower('email'),
                name='user_email_ci_uniqueness',
            ),
        ]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)


class InviteCode(models.Model):

    sender = models.ForeignKey(
        User,
        verbose_name='Отправитель',
        related_name='invitations',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    email = models.EmailField(
        unique=True,
        max_length=254
    )
    code = models.UUIDField(
        unique=True,
        default=uuid.uuid4
    )
    created = models.DateTimeField(
        verbose_name='Дата отправки инвайта',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Приглашение'
        verbose_name_plural = 'Приглашения'
        ordering = ['-created']

    def __str__(self):
        return f'invite_{self.pk} to {self.email}'

    def expire_date(self):
        return self.created + timezone.timedelta(
            days=settings.INVITE_TIME_EXPIRES_DAYS)

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    expire_date.short_description = 'Дата окончания инвайта'


class PasswordResetCode(models.Model):

    email = models.EmailField(
        unique=True,
        max_length=254
    )
    code = models.UUIDField(
        unique=True,
        default=uuid.uuid4
    )
    created = models.DateTimeField(
        verbose_name='Дата отправки кода',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Сброс пароля'
        verbose_name_plural = 'Сбросы паролей'
        ordering = ['-created']

    def __str__(self):
        return f'reset_{self.pk} to {self.email}'

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)
