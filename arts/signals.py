from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import Exhibition, Artwork, Artist

@receiver(post_save, sender=Exhibition)
def update_exhibition_search_vector(sender, instance, **kwargs):
    Exhibition.objects.filter(id=instance.id).update(
        search_vector=SearchVector('title', 'description', 'categories')
    )

@receiver(post_save, sender=Artwork)
def update_artwork_search_vector(sender, instance, **kwargs):
    Artwork.objects.filter(id=instance.id).update(
        search_vector=SearchVector('title', 'description', 'medium')
    )

@receiver(post_save, sender=Artist)
def update_artist_search_vector(sender, instance, **kwargs):
    Artist.objects.filter(id=instance.id).update(
        search_vector=SearchVector('name', 'bio', 'nationality')
    ) 