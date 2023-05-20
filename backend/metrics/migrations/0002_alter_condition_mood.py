# Generated by Django 4.2.1 on 2023-05-19 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='condition',
            name='mood',
            field=models.CharField(choices=[('Bad', 'Плохо'), ('So so', 'Так себе'), ('OK', 'Нормально'), ('Fine', 'Хорошо'), ('Good', 'Отлично')], max_length=9, verbose_name='Настроение'),
        ),
    ]
