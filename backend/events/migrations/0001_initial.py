# Generated by Django 4.2.1 on 2023-06-12 10:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
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
                    "name",
                    models.CharField(
                        max_length=48,
                        unique=True,
                        validators=[django.core.validators.MinLengthValidator(2)],
                        verbose_name="Наименование",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(max_length=32, unique=True, verbose_name="Слаг"),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        max_length=254,
                        null=True,
                        validators=[django.core.validators.MinLengthValidator(8)],
                        verbose_name="Описание",
                    ),
                ),
            ],
            options={
                "verbose_name": "Категория",
                "verbose_name_plural": "Категории",
            },
        ),
        migrations.CreateModel(
            name="Entry",
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
                        max_length=128,
                        validators=[django.core.validators.MinLengthValidator(2)],
                        verbose_name="Заголовок",
                    ),
                ),
                (
                    "preview_image",
                    models.ImageField(
                        upload_to="entries/", verbose_name="Превью-изображение записи"
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        validators=[django.core.validators.MinLengthValidator(8)],
                        verbose_name="Текст",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Запись",
                "verbose_name_plural": "Записи",
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="Event",
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
                    "name",
                    models.CharField(
                        max_length=64,
                        validators=[django.core.validators.MinLengthValidator(2)],
                        verbose_name="Наименование",
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        max_length=128,
                        validators=[django.core.validators.MinLengthValidator(8)],
                        verbose_name="Текст",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "start_time",
                    models.DateTimeField(verbose_name="Дата и время начала"),
                ),
                (
                    "end_time",
                    models.DateTimeField(verbose_name="Дата и время окончания"),
                ),
            ],
            options={
                "verbose_name": "Событие",
                "verbose_name_plural": "События",
                "ordering": ["-created"],
            },
        ),
    ]
