from django.contrib import admin

from .models import Category, Entry, Event


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'description',)
    list_display = fields


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    fields = ('created', 'title', 'preview_image',
              'author', 'category', 'description', 'url', 'text',)
    list_display = ('created', 'title', 'description',
                    'preview_image', 'author')
    readonly_fields = ('created',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = ('created', 'name', 'author', 'text', 'for_all', 'employees',
              'departments', 'start_time', 'end_time',)
    list_display = ('created', 'name', 'author',
                    'start_time', 'end_time', 'for_all')
    readonly_fields = ('created',)
