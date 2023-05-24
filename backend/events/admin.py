from django.contrib import admin

from .models import Category, Entry, Event


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'description',)
    list_display = fields


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    fields = ('created', 'title', 'preview_image',
              'author', 'category', 'text',)
    list_display = ('created', 'title', 'preview_image', 'author', 'category')
    readonly_fields = ('created',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = ('created', 'name', 'author', 'employees',
              'departments', 'start_time', 'end_time',)
    list_display = ('created', 'name', 'author', 'start_time', 'end_time',)
    readonly_fields = ('created',)
