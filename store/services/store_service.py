from typing import Optional, List
from decimal import Decimal
from store.infra.respository import StoreRepository
from store.models import Item, Purchase
from users.domain.entities.user_entity import UserEntity
from store.helpers.payment_gateway import PaymentGateway

class StoreService:
    def __init__(self, store_repository: Optional[StoreRepository] = None):
        self.store_repository = store_repository or StoreRepository()

    #Items
    def list_item(self)-> List[Item]:
        return self.store_repository.list_items()
    
    def get_items(self, item_id: str) -> Optional[Item]:
        return self.store_repository.get_item_by_id(id=item_id)
    
    def search_items(self, name:str) -> List[Item]:
        return self.store_repository.search_by_name(name=name)
    
    def get_by_category(self, category_id: str) -> List[Item]:
        return self.store_repository.get_by_category(category_id=category_id)
    
    def create_item(self, item_data) -> Item:
        item = Item(**item_data)
        return self.store_repository.create_item(item=item)
    
    def update_item(self, item_id: str, data) -> Optional[Item]:
        item = self.store_repository.get_item_by_id(id=item_id)

        if not item:
            return None
        
        for k, v in data.items():
            setattr(item, k, v)
        return self.store_repository.update_item(item=item)
    
    def delete_item(self, item_id: str) -> bool:
        return self.store_repository.delete_item(item_id=item_id)
    
    #Favoritos
    def add_favorites(self, user, item_id: str):
        item = self.store_repository.get_item_by_id(id=item_id)

        if not item:
            return None
        return self.store_repository.add_favorite(user=user, item=item)
    
    def remove_favorite(self, user, item_id:str) -> bool:
        item = self.store_repository.get_item_by_id(id=item_id)

        if not item:
            return False
        return self.store_repository.remove_favorite(user=user, item=item)
        
    def list_favorites(self, user):
        return self.store_repository.list_favorites(user=user)
    
    #cart
    def add_to_cart(self, user, item_id: str, quantity: int):
        item = self.store_repository.get_item_by_id(id=item_id)

        if not item:
            return None
        
        if item.stock < quantity:
            raise ValueError("Not enough stock")
        
        return self.store_repository.add_cart_item(user=user, item=item_id, quantity=quantity)
    
    def remove_from_cart(self, user, item_id: str):
        item = self.store_repository.get_item_by_id(id=item_id)

        if not item:
            return False
        return self.store_repository.remove_cart_item(user=user, item=item_id)
    
    def list_cart(self, user):
        return self.store_repository.list_cart(user=user)
    
    def purchase_item(self, user, item_id: str, quantity: int, payment_method:str, payment_proof_file, shipping_data: dict) -> Optional[Purchase]:
        item = self.store_repository.get_item_by_id(id=item_id)

        if not item:
            return None
        
        if item.stock < quantity:
            raise ValueError("Not enough stock")
            
        total = item.price * Decimal(quantity)

        amount = float(total)

        payment_simulator = PaymentGateway.process_payment(method=payment_method, amount=amount)

        if not payment_simulator:
            raise ValueError("Payment failed")
        
        purchase = Purchase(
            user=user,
            item=item,
            quantity=quantity,
            total_price=total,
            payment_method=payment_method,
            payment_proof=payment_proof_file,
            first_name=shipping_data["first_name"],
            las_name=shipping_data["last_name"],
            city=shipping_data["city"],
            country=shipping_data["country"],
            street_address=shipping_data["street_address"],
            house_number=shipping_data["house_number"],
            phone=shipping_data["phone"],
            email=shipping_data["email"],
        )

        return self.store_repository.create_purchase(purchase)

