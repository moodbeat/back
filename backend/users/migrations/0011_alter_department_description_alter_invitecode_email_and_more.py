# Generated by Django 4.2.1 on 2023-05-18 11:02

import django.core.validators
from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0010_alter_invitecode_options_alter_user_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="department",
            name="description",
            field=models.TextField(
                blank=True, max_length=254, null=True, verbose_name="Описание"
            ),
        ),
        migrations.AlterField(
            model_name="invitecode",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name="position",
            name="description",
            field=models.TextField(
                blank=True, max_length=254, null=True, verbose_name="Описание"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="about",
            field=models.TextField(
                blank=True,
                max_length=256,
                null=True,
                validators=[django.core.validators.MinLengthValidator(2)],
                verbose_name="О себе",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=254,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(8)],
                verbose_name="email",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                max_length=32,
                validators=[
                    users.validators.validate_first_name,
                    django.core.validators.MinLengthValidator(2),
                ],
                verbose_name="first name",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(
                max_length=32,
                validators=[
                    users.validators.validate_last_name,
                    django.core.validators.MinLengthValidator(2),
                ],
                verbose_name="last name",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="patronymic",
            field=models.CharField(
                blank=True,
                max_length=32,
                null=True,
                validators=[
                    users.validators.validate_patronymic,
                    django.core.validators.MinLengthValidator(2),
                ],
                verbose_name="Отчество",
            ),
        ),
    ]