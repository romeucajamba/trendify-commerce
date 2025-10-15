from django.core.cache import cache
from store.models import Item
from store.serializers import ItemSerializer

class ProductCacheService:
    CACHE_KEY = "featured_products"

    @staticmethod
    def get_featured_products():
        products = cache.get(ProductCacheService.CACHE_KEY)
        # Assim, estou garantindo que o cache armazene JSON (serializável) — e evita problemas de pickle com o ORM
        if products is None:
            print("Cache miss: fetching from DB")
            queryset = Item.objects.all()
            serializer = ItemSerializer(queryset, many=True)
            products = serializer.data
            cache.set(ProductCacheService.CACHE_KEY, products, timeout=60*5)
        else: print("Cache hit: fetching from cache")
        
        return products
