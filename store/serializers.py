from rest_framework import serializers 
from .models import Category, Item, Favorite, CartItem, Purchase

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]

class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only= True)

    class Meta:
        model = Item
        fields = ["id", "name", "description", "price", "category", "stock", "created_at", "updated_at"]

class ItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["name", "description", "price", "category", "stock", "image"]

class FavoriteSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "item", "created_at"]

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "item", "quantity", "added_at"]

class CartAddSerializer(serializers.ModelSerializer):
    item_id = serializers.UUIDField()
    quatity = serializers.IntegerField(min_value=1)


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        read_only_fields = ["id", "total_price", "created_at"]
        fields = [
            "id",
            "item",
            "quantity",
            "total_price",
            "payment_method",
            "payment_proof",
            "first_name",
            "last_name",
            "city",
            "country",
            "street_address",
            "house_number",
            "phone",
            "email",
            "created_at",
        ]
    
    def validate(self, data):
        if data.get("quantity", 1) < 1:
            raise serializers.ValidationError({"quantity": "Quantity must be at last 1"})
        return data

