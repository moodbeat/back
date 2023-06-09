# Generated by Django 4.2.1 on 2023-06-07 14:10

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_remove_user_avatar_thumbnail"),
    ]

    operations = [
        migrations.CreateModel(
            name="MentalState",
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
                        max_length=128,
                        validators=[django.core.validators.MinLengthValidator(2)],
                        verbose_name="Наименование",
                    ),
                ),
                ("slug", models.SlugField(verbose_name="Слаг")),
                (
                    "description",
                    models.TextField(
                        blank=True, max_length=512, null=True, verbose_name="Описание"
                    ),
                ),
            ],
            options={
                "verbose_name": "Психологическое состояние",
                "verbose_name_plural": "Психологические состояния",
            },
        ),
        migrations.AlterField(
            model_name="user",
            name="mental_state",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="users.mentalstate",
                verbose_name="Психологическое состояние",
            ),
        ),
    ]
