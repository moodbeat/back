# Generated by Django 4.2.1 on 2023-07-18 17:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("events", "0001_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="meetingresult",
            name="employee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="meets",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Сотрудник",
            ),
        ),
        migrations.AddField(
            model_name="meetingresult",
            name="mental_state",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="meets",
                to="users.mentalstate",
                verbose_name="Состояние",
            ),
        ),
        migrations.AddField(
            model_name="meetingresult",
            name="organizer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organized_meets",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Организатор",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="authored_events",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="departments",
            field=models.ManyToManyField(
                blank=True,
                related_name="events",
                to="users.department",
                verbose_name="Отдел(ы)",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="employees",
            field=models.ManyToManyField(
                blank=True,
                related_name="participated_events",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Сотрудники",
            ),
        ),
        migrations.AddField(
            model_name="entry",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="entries",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AddField(
            model_name="entry",
            name="category",
            field=models.ManyToManyField(
                blank=True,
                related_name="entries",
                to="events.category",
                verbose_name="Категория",
            ),
        ),
    ]
