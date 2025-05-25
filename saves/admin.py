from django.contrib import admin
from .models import SaveFolder, SaveItem

@admin.register(SaveFolder)
class SaveFolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user',)
    search_fields = ('name', 'description', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(SaveItem)
class SaveItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'folder', 'item_type', 'item_id', 'created_at')
    list_filter = ('item_type', 'folder', 'user')
    search_fields = ('notes', 'user__username', 'folder__name')
    date_hierarchy = 'created_at'
