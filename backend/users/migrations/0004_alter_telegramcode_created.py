# Generated by Django 4.2.1 on 2023-07-19 12:59

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_telegramcode_created"),
    ]

    operations = [
        migrations.AlterField(
            model_name="telegramcode",
            name="created",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Время отправки кода"
            ),
        ),
    ]
