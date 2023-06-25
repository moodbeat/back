from django.contrib import admin

from .models import HelpType, Like, NeedHelp, Status


@admin.register(HelpType)
class HelpTypeAdmin(admin.ModelAdmin):
    fields = ('title', 'role')
    list_display = fields


@admin.register(NeedHelp)
class NeedHelpAdmin(admin.ModelAdmin):
    fields = ('created', 'sender', 'recipient', 'type', 'viewed')
    list_display = fields
    readonly_fields = ('created',)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    fields = ('created', 'author', 'text', 'views', 'likes')
    list_display = ('created', 'text', 'views', 'likes')
    readonly_fields = ('created',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    fields = ('created', 'author', 'event', 'entry',)
    list_display = ('created', 'author', 'event', 'entry',)
    readonly_fields = ('created',)
