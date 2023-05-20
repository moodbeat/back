# import datetime
#
# from django.contrib.auth import get_user_model
# from django.db import models
# from events.validators import validate_time
#
# User = get_user_model()
#
#
# class Category(models.Model):
#     name = models.CharField(
#         verbose_name='Наименование',
#         max_length=255,
#     )
#     description = models.TextField(
#         verbose_name='Описание',
#         max_length=500,
#         null=True,
#         blank=True
#     )
#
#     class Meta:
#         verbose_name = 'Категория'
#         verbose_name_plural = 'Категории'
#
#     def __str__(self):
#         return self.name
#
#
# class Entry(models.Model):
#     author = models.ForeignKey(
#         User,
#         verbose_name='Автор',
#         related_name='entries',
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL
#     )
#
#     description = models.TextField(
#         verbose_name='Описание',
#         max_length=500,
#         null=True,
#         blank=True
#     )
#
#     text = models.TextField(
#         verbose_name='Описание',
#         max_length=500
#     )
#
#     category = models.ForeignKey(
#         Category,
#         verbose_name='Категория',
#         related_name='categories',
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL
#     )
#
#     created = models.DateTimeField(
#         default=datetime.datetime.now()
#     )
#
#     delayed_publication = models.DateTimeField(
#         null=True,
#         blank=True
#     )
#
#     class Meta:
#         verbose_name = 'Должность'
#         verbose_name_plural = 'Должности'
#
#     def __str__(self):
#         return self.name
#
#
# class Event(models.Model):
#     author = models.ForeignKey(
#         User,
#         verbose_name='Автор',
#         related_name='events',
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL
#     )
#     name = models.CharField(
#         verbose_name='Наименование',
#         max_length=255,
#     )
#     created = models.DateTimeField(
#         default=datetime.datetime.now()
#     )
#     start_date = models.DateTimeField(
#         verbose_name='Дата начала события',
#         validators=[validate_time]
#     )
#     end_date = models.DateTimeField(
#         verbose_name='Дата окончания события',
#         validators=[validate_time]
#     )
#     # confirm_required =
#
#
# class EventResponse(models.Model):
#     employee = models.ForeignKey(
#         User,
#         verbose_name='Сотрудник',
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL
#     )
#     event = models.ForeignKey(
#         Event,
#         verbose_name='Событие',
#         on_delete=models.CASCADE
#     )
#     date_time_response = models.DateTimeField(
#         verbose_name='Дата и время отклика',
#         auto_now_add=True,
#     )
