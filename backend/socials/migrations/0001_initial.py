# Generated by Django 4.2.1 on 2023-06-28 16:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="HelpType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        max_length=32,
                        unique=True,
                        validators=[django.core.validators.MinLengthValidator(2)],
                        verbose_name="Тип помощи",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        max_length=128,
                        null=True,
                        validators=[django.core.validators.MinLengthValidator(8)],
                        verbose_name="Описание",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        blank=True,
                        choices=[("hr", "HR"), ("chief", "Руководитель")],
                        max_length=10,
                        null=True,
                        verbose_name="Роль",
                    ),
                ),
            ],
            options={
                "verbose_name": "Тип помощи",
                "verbose_name_plural": "Типы помощи",
            },
        ),
        migrations.CreateModel(
            name="Like",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата и время"
                    ),
                ),
            ],
            options={
                "verbose_name": "Лайк",
                "verbose_name_plural": "Лайки",
            },
        ),
        migrations.CreateModel(
            name="NeedHelp",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "comment",
                    models.TextField(
                        max_length=496,
                        validators=[django.core.validators.MinLengthValidator(4)],
                        verbose_name="Комментарий",
                    ),
                ),
                (
                    "viewed",
                    models.BooleanField(default=False, verbose_name="Просмотрено"),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата и время отправки"
                    ),
                ),
            ],
            options={
                "verbose_name": "Запрос помощи",
                "verbose_name_plural": "Запросы помощи",
            },
        ),
        migrations.CreateModel(
            name="Status",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        max_length=320,
                        validators=[django.core.validators.MinLengthValidator(4)],
                        verbose_name="Текст",
                    ),
                ),
                (
                    "views",
                    models.PositiveIntegerField(default=0, verbose_name="Просмотров"),
                ),
                ("likes", models.IntegerField(default=0, verbose_name="Понравилось")),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата и время отправки"
                    ),
                ),
            ],
            options={
                "verbose_name": "Статус",
                "verbose_name_plural": "Статусы",
                "ordering": ["-created"],
            },
        ),
    ]
