from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Item
from django.core.cache import cache
from store.services.cache_service import ProductCacheService

@receiver(post_save, sender=Item)
def clear_featured_cache(sender, instance, **kwargs):
    cache.delete(ProductCacheService.CACHE_KEY)
    print(f"Cache cleared due to save: {instance.id}")

def clear_cache_on_item_delete(sender, instance, **kwargs):
    cache.delete(ProductCacheService.CACHE_KEY)
    print(f"Cache cleared due to delete: {instance.id}")