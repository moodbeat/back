# Generated by Django 4.2.1 on 2023-05-19 22:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_alter_entry_created_alter_event_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 20, 1, 59, 25, 883920)),
        ),
        migrations.AlterField(
            model_name='event',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 20, 1, 59, 25, 883920)),
        ),
    ]
