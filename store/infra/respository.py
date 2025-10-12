from typing import Optional, List, UserIdType
from store.models import Item, Category, CartItem, Favorite, Purchase
from users.domain.entities.user_entity import UserEntity

class StoreRepository:
    #Item
    def get_item_by_id(self, id: str) -> Optional[Item]:
        try:
            return Item.objects.filter(id=id).first()
        except Exception:
            return None
    
    def list_items(self) -> List[Item]:
        return list(Item.objects.all().order_by("created_at"))
    
    def search_by_name(self, name: str) -> List[Item]:
        return list(Item.objects.filter(name__icontains=name))
    
    def get_by_category(self, category_id: str) -> List[Item]:
        return list(Item.objects.filter(category_id=category_id))
    
    def create_item(self, item: Item) ->  Item:
        item.save()
        return item

    def update_item(self, item: Item) -> Item:
        item.save()
        return item
    
    def delete_item(self, item_id: str) ->  bool:
        deleted, _ = Item.objects.filter(id=item_id).delete()

        return deleted > 0
    
    #Favorites
    def add_favorite(self, user, item) -> Favorite:
        fav, _ = Favorite.objects.filter(user=user, item=item)

        return fav
    
    def remove_favorite(self, user, item) -> bool:
        deleted, _ = Favorite.objects.filter(user=user, item=item).delete()
        
        return deleted > 0
    
    def list_favorites(seld, user) -> List[Favorite]:
        return list(Favorite.objects.filter(user=user).select_related("item"))
    
    #Cart
    def add_cart_item(self, user, item, quantity) -> CartItem:
        cart_item, created = CartItem.objects.get_or_create(user=user, item=item)

        if not created:
            cart_item.quatity += quantity
        else:
            cart_item.quatity = quantity
            cart_item.save()

            return cart_item
    
    def remove_cart_item(self, user, item) -> bool:
        deleted, _ = CartItem.objects.filter(user=user, item=item).delete()

        return deleted > 0
    
    def list_cart(self, user) -> List[CartItem]:
        return list(CartItem.objects.filter(user=user).select_related("item"))
    
    #purchase
    def create_purchase(self, purchase: Purchase) -> Purchase:
        purchase.save()
        return purchase