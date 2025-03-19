from django.contrib import admin
from .models import (
    User, Artist, Museum, Exhibition, Artwork, 
    Docent, Highlight, Like, Collection, CollectionItem
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'nickname', 'email', 'date_joined')
    search_fields = ('username', 'nickname', 'email')

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'nationality', 'birth_year', 'death_year')
    search_fields = ('name', 'nationality')
    list_filter = ('nationality',)

@admin.register(Museum)
class MuseumAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'address')
    search_fields = ('name', 'city')
    list_filter = ('city',)

@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'museum', 'start_date', 'end_date', 'is_public')
    search_fields = ('title', 'museum__name')
    list_filter = ('is_public', 'museum')
    date_hierarchy = 'start_date'

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'year', 'medium')
    search_fields = ('title', 'artist__name')
    list_filter = ('medium', 'exhibition')

@admin.register(Docent)
class DocentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'exhibition', 'created_at', 'is_public')
    search_fields = ('title', 'author__username', 'exhibition__title')
    list_filter = ('is_public', 'exhibition')
    date_hierarchy = 'created_at'

@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('user', 'artwork', 'created_at')
    search_fields = ('user__username', 'artwork__title')
    list_filter = ('artwork__exhibition',)
    date_hierarchy = 'created_at'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('content_type',)
    date_hierarchy = 'created_at'

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_public', 'created_at')
    search_fields = ('name', 'user__username')
    list_filter = ('is_public',)
    date_hierarchy = 'created_at'

@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ('collection', 'item_type', 'object_id', 'created_at')
    search_fields = ('collection__name',)
    list_filter = ('item_type', 'collection__user')
    date_hierarchy = 'created_at' 