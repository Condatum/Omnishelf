from django.contrib import admin

from .models import Folder, Tag


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'sort_order', 'color_hex')
    list_filter = ('user',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'user', 'color_hex')
    list_filter = ('user',)
    search_fields = ('name', 'slug')
