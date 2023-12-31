# Generated by Django 4.2.1 on 2023-07-21 00:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("metrics", "0001_initial"),
        ("users", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="userlifebalance",
            name="employee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="life_balance",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Сотрудник",
            ),
        ),
        migrations.AddField(
            model_name="survey",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор опроса",
            ),
        ),
        migrations.AddField(
            model_name="survey",
            name="department",
            field=models.ManyToManyField(
                blank=True, to="users.department", verbose_name="Отделы"
            ),
        ),
        migrations.AddField(
            model_name="survey",
            name="type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="metrics.surveytype",
                verbose_name="Тип опроса",
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="survey",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="metrics.survey",
                verbose_name="Опрос",
            ),
        ),
        migrations.AddField(
            model_name="condition",
            name="employee",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Сотрудник",
            ),
        ),
        migrations.AddField(
            model_name="completedsurvey",
            name="employee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="survey_results",
                to=settings.AUTH_USER_MODEL,
                verbose_name="сотрудник",
            ),
        ),
        migrations.AddField(
            model_name="completedsurvey",
            name="mental_state",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="users.mentalstate",
                verbose_name="Оценка состояния",
            ),
        ),
        migrations.AddField(
            model_name="completedsurvey",
            name="survey",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="metrics.survey",
                verbose_name="опрос",
            ),
        ),
        migrations.AddField(
            model_name="burnouttracker",
            name="employee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="burnout_track",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Сотрудник",
            ),
        ),
        migrations.AddField(
            model_name="burnouttracker",
            name="mental_state",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="burnout_track",
                to="users.mentalstate",
                verbose_name="Состояние",
            ),
        ),
        migrations.AddField(
            model_name="activitytracker",
            name="employee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="activity_trackers",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Сотрудник",
            ),
        ),
        migrations.AddField(
            model_name="activityrate",
            name="tracker",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="activity_rates",
                to="metrics.activitytracker",
                verbose_name="Трекер",
            ),
        ),
        migrations.AddField(
            model_name="activityrate",
            name="type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="metrics.activitytype",
                verbose_name="Тип деятельности",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="activityrate",
            unique_together={("type", "tracker")},
        ),
    ]
