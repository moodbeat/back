# Generated by Django 4.2.1 on 2023-07-19 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_telegramcode_telegramuser"),
    ]

    operations = [
        migrations.AlterField(
            model_name="telegramcode",
            name="created",
            field=models.DateTimeField(
                auto_now=True, verbose_name="Время отправки кода"
            ),
        ),
    ]
