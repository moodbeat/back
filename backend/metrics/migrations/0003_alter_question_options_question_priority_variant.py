# Generated by Django 4.2.1 on 2023-06-10 15:46

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("metrics", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="question",
            options={
                "ordering": ("priority", "id"),
                "verbose_name": "Вопрос",
                "verbose_name_plural": "Вопросы",
            },
        ),
        migrations.AddField(
            model_name="question",
            name="priority",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(99),
                ],
                verbose_name="Приоритет при выдаче",
            ),
        ),
        migrations.CreateModel(
            name="Variant",
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
                    models.CharField(max_length=255, verbose_name="Текст варианта"),
                ),
                (
                    "priority",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(99),
                        ],
                        verbose_name="Приоритет при выдаче",
                    ),
                ),
                (
                    "for_type",
                    models.BooleanField(default=False, verbose_name="Типовой вопрос"),
                ),
                (
                    "value",
                    models.IntegerField(blank=True, null=True, verbose_name="Значение"),
                ),
                (
                    "survey_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="metrics.surveytype",
                        verbose_name="Тип опроса",
                    ),
                ),
            ],
            options={
                "verbose_name": "Вариант ответа",
                "verbose_name_plural": "Варианты ответа",
                "ordering": ("priority", "id"),
            },
        ),
    ]
