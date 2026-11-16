from django.contrib import admin

from .models import Folder, LibraryEntry, ReadingSnapshot, Tag


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


@admin.register(LibraryEntry)
class LibraryEntryAdmin(admin.ModelAdmin):
    list_display = ('custom_title', 'user', 'chapter_label', 'status', 'source_domain', 'last_read_at')
    list_filter = ('status', 'source_domain', 'user')
    search_fields = ('custom_title', 'original_source_title', 'current_uri')


@admin.register(ReadingSnapshot)
class ReadingSnapshotAdmin(admin.ModelAdmin):
    list_display = ('entry', 'chapter_label', 'uri', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('uri', 'chapter_label')
