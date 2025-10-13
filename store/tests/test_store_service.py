from django.test import TestCase
from unittest.mock import patch, MagicMock
from decimal import Decimal
from store.services.store_service import StoreService
from store.models import Item
from django.contrib.auth import get_user_model


class TestStoreService(TestCase):
    """
    Testes unitários para o serviço StoreService usando o banco de testes do Django.
    """

    @classmethod
    def setUpTestData(cls):
        """Cria dados persistentes que são compartilhados entre todos os testes."""
        User = get_user_model()
        cls.sample_user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )

    def setUp(self):
        """Executa antes de cada teste individual."""
        self.mock_repo = MagicMock()
        self.store_service = StoreService(store_repository=self.mock_repo)
        self.sample_user = self.__class__.sample_user  # ✅ agora garantido

        # Item fictício
        self.sample_item = Item(
            id="item-1",
            name="Test Item",
            description="Desc",
            price=Decimal("10.0"),
            stock=5,
            category=None
        )

    #        ITEMS

    def test_list_item(self):
        self.mock_repo.list_items.return_value = ["item1", "item2"]
        items = self.store_service.list_item()
        self.assertEqual(items, ["item1", "item2"])
        self.mock_repo.list_items.assert_called_once()

    def test_get_items(self):
        self.mock_repo.get_item_by_id.return_value = self.sample_item
        item = self.store_service.get_items("item-1")
        self.assertEqual(item, self.sample_item)
        self.mock_repo.get_item_by_id.assert_called_once_with(id="item-1")

    def test_search_items(self):
        self.mock_repo.search_by_name.return_value = ["item1"]
        results = self.store_service.search_items("item")
        self.assertEqual(results, ["item1"])
        self.mock_repo.search_by_name.assert_called_once_with(name="item")

    def test_create_item(self):
        data = {
            "name": "New Item",
            "description": "Desc",
            "price": Decimal("5.0"),
            "stock": 10,
            "category": None
        }
        self.mock_repo.create_item.return_value = "created_item"
        item = self.store_service.create_item(data)
        self.assertEqual(item, "created_item")
        self.mock_repo.create_item.assert_called_once()

    def test_update_item_success(self):
        self.mock_repo.get_item_by_id.return_value = self.sample_item
        self.mock_repo.update_item.return_value = "updated_item"
        updated = self.store_service.update_item("item-1", {"name": "Updated"})
        self.assertEqual(updated, "updated_item")
        self.mock_repo.update_item.assert_called_once()

    def test_update_item_not_found(self):
        self.mock_repo.get_item_by_id.return_value = None
        updated = self.store_service.update_item("item-1", {"name": "Updated"})
        self.assertIsNone(updated)

    def test_delete_item(self):
        self.mock_repo.delete_item.return_value = True
        result = self.store_service.delete_item("item-1")
        self.assertTrue(result)
        self.mock_repo.delete_item.assert_called_once_with(item_id="item-1")

    #        FAVORITES

    def test_add_favorites_success(self):
        self.mock_repo.get_item_by_id.return_value = self.sample_item
        self.mock_repo.add_favorite.return_value = "favorite"
        fav = self.store_service.add_favorites(self.sample_user, "item-1")
        self.assertEqual(fav, "favorite")

    def test_add_favorites_item_not_found(self):
        self.mock_repo.get_item_by_id.return_value = None
        fav = self.store_service.add_favorites(self.sample_user, "item-1")
        self.assertIsNone(fav)

    def test_remove_favorite_success(self):
        self.mock_repo.get_item_by_id.return_value = self.sample_item
        self.mock_repo.remove_favorite.return_value = True
        result = self.store_service.remove_favorite(self.sample_user, "item-1")
        self.assertTrue(result)

    def test_remove_favorite_item_not_found(self):
        self.mock_repo.get_item_by_id.return_value = None
        result = self.store_service.remove_favorite(self.sample_user, "item-1")
        self.assertFalse(result)

    #          CART

    def test_add_to_cart_success(self):
        self.mock_repo.get_item_by_id.return_value = self.sample_item
        self.mock_repo.add_cart_item.return_value = "cart_item"
        result = self.store_service.add_to_cart(self.sample_user, "item-1", 2)
        self.assertEqual(result, "cart_item")

    def test_add_to_cart_not_enough_stock(self):
        self.mock_repo.get_item_by_id.return_value = self.sample_item
        with self.assertRaises(ValueError):
            self.store_service.add_to_cart(self.sample_user, "item-1", 10)

    def test_add_to_cart_item_not_found(self):
        self.mock_repo.get_item_by_id.return_value = None
        result = self.store_service.add_to_cart(self.sample_user, "item-1", 1)
        self.assertIsNone(result)

    def test_remove_from_cart_success(self):
        self.mock_repo.get_item_by_id.return_value = self.sample_item
        self.mock_repo.remove_cart_item.return_value = True
        result = self.store_service.remove_from_cart(self.sample_user, "item-1")
        self.assertTrue(result)

    def test_remove_from_cart_item_not_found(self):
        self.mock_repo.get_item_by_id.return_value = None
        result = self.store_service.remove_from_cart(self.sample_user, "item-1")
        self.assertFalse(result)

    #         PURCHASE

    @patch("store.services.store_service.PaymentGateway.process_payment")
    def test_purchase_item_success(self, mock_payment):
        self.mock_repo.get_item_by_id.return_value = self.sample_item
        self.mock_repo.create_purchase.return_value = "purchase"
        mock_payment.return_value = True

        shipping_data = {
            "first_name": "Romeu",
            "last_name": "Cajamba",
            "city": "Luanda",
            "country": "Angola",
            "street_address": "Sambizanga",
            "house_number": "Zona 13 CASA S/Nº",
            "phone": "123456789",
            "email": "romeu@example.com",
        }

        result = self.store_service.purchase_item(
            self.sample_user, "item-1", 2, "credit", "file.pdf", shipping_data
        )

        self.assertEqual(result, "purchase")
        mock_payment.assert_called_once()

    def test_purchase_item_not_enough_stock(self):
        self.mock_repo.get_item_by_id.return_value = self.sample_item
        with self.assertRaises(ValueError):
            self.store_service.purchase_item(
                self.sample_user, "item-1", 10, "credit", "file.pdf", {}
            )

    def test_purchase_item_item_not_found(self):
        self.mock_repo.get_item_by_id.return_value = None
        result = self.store_service.purchase_item(
            self.sample_user, "item-1", 1, "credit", "file.pdf", {}
        )
        self.assertIsNone(result)

    @patch("store.services.store_service.PaymentGateway.process_payment")
    def test_purchase_item_payment_failed(self, mock_payment):
        self.mock_repo.get_item_by_id.return_value = self.sample_item
        mock_payment.return_value = False

        with self.assertRaises(ValueError):
            self.store_service.purchase_item(
                self.sample_user,
                "item-1",
                1,
                "credit",
                "file.pdf",
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "city": "City",
                    "country": "Country",
                    "street_address": "Street",
                    "house_number": "123",
                    "phone": "123456789",
                    "email": "john@example.com",
                },
            )
