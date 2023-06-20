# Generated by Django 4.2.1 on 2023-06-20 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="entry",
            name="category",
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
