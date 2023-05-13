import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .managers import UserManager


class Department(models.Model):

    name = models.CharField(
        verbose_name='Наименование',
        max_length=255,
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=500,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'

    def __str__(self):
        return self.name


class Position(models.Model):

    name = models.CharField(
        verbose_name='Название должности',
        max_length=255,
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=500,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.name


class Hobby(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True
    )

    class Meta:
        verbose_name = 'Список интересов'
        verbose_name_plural = 'Списки интересов'

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
        max_length=255
    )
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=120
    )
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=120
    )
    patronymic = models.CharField(
        verbose_name='Отчество',
        max_length=120,
        blank=True,
        null=True
    )
    department = models.ForeignKey(
        Department,
        verbose_name='Отдел',
        related_name='employees',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_index=True
    )
    position = models.ForeignKey(
        Position,
        verbose_name='Должность',
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
    avatar = models.ImageField(
        verbose_name='Аватар/Фото',
        upload_to='users/avatars/',
        blank=True,
        null=True
    )
    about = models.TextField(
        verbose_name='О себе',
        max_length=500,
        blank=True,
        null=True
    )
    phone = PhoneNumberField(
        verbose_name='Телефон',
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

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class InviteCode(models.Model):

    email = models.EmailField(
        unique=True,
        max_length=255
    )
    code = models.UUIDField(
        unique=True,
        default=uuid.uuid4
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.token
