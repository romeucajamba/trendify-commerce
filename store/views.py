from rest_framework import status, permissions
from rest_framework.response import Response
from typing import Any, Dict, cast
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from store.services.store_service import StoreService
from store.services.cache_service import ProductCacheService
from store.serializers import (
    ItemSerializer, ItemCreateUpdateSerializer,
    FavoriteSerializer, CartItemSerializer, 
    CartAddSerializer, PurchaseSerializer, PurchaseRequestSerializer
)
from store.models import Item, Favorite, CartItem, Purchase
from store.helpers.errors.error import ( DatabaseError, NotFoundError, UnauthorizedError, BadRequestError, AppError) 


store_service = StoreService()

class AuthenticatedAPIView(APIView):
    def dispatch(self, request, *args, **kwargs):
        if getattr(request, "user_id", None) is None:
            raise UnauthorizedError(
                safe_message="Authentication required",
                status_code=401,
                code="unauthorized"
            )
        return super().dispatch(request, *args, **kwargs)
    

class ItemListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="List all items",
        operation_description="Returns a list of items. Public endpoint.",
        responses={200: ItemSerializer(many=True)},
        tags=["Store - Items"]
    )
    def get(self, request):
        try:
            items = store_service.list_item()
            serializer = ItemSerializer(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AppError:
            raise
        except Exception:
            raise DatabaseError(safe_message="An unexpected error occurred while fetching items.", code="internal_error", status_code=500)   

    @swagger_auto_schema(
        operation_summary="Create a new store item",
        operation_description="Create a new store item (Requires authentication).",
        request_body=ItemCreateUpdateSerializer,
        manual_parameters=[],
        consumes=["multipart/form-data"],
        responses={
            201: ItemSerializer(),
            400: "Invalid input data",
            401:"Unauthorized",
            500: "Internal server error"
        },
        tags=["Store - Items"]
    )
    def post(self, request):
        try:
            serializer = ItemCreateUpdateSerializer(data=request.data)
            
            if not serializer.is_valid():
                raise BadRequestError(safe_message="Ivalid data", extra=serializer.errors, code="bad_request", status_code=400)

            item = store_service.create_item(serializer.validated_data)
            
            return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)
        
        except AppError: raise
        except Exception: raise DatabaseError(safe_message="An unexpected error occurred.", code="internal_error", status_code=500)

class FeaturedItemView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Get featured items",
        responses={200: ItemSerializer(many=True)},
        tags=["Store - Items"]
    )
    def get(self, request):
        products = ProductCacheService.get_featured_products()
        return Response(products, status=status.HTTP_200_OK)

class ItemDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Get item by id",
        responses={
            200: ItemSerializer(),
            404: "Item not found",
            500: "Internal server error",
        },
        tags=["Store - Items"],
    )
    def get(self, request, item_id: str):
        try:
            item = store_service.get_items(item_id)
            if not item:
                raise NotFoundError(safe_message="Item not found", status_code=404, code="not_found")
            return Response(ItemSerializer(item).data, status=status.HTTP_200_OK)
        except AppError:
            raise
        except Exception:
            raise DatabaseError(safe_message="An unexpected error occurred.", code="internal_error", status_code=500)

    @swagger_auto_schema(
        operation_summary="Update an item",
        request_body=ItemCreateUpdateSerializer,
        manual_parameters=[],
        consumes=["multipart/form-data"],
        responses={
            200: ItemSerializer(),
            400: "Invalid data",
            404: "Item not found",
            500: "Internal server error",
        },
        tags=["Store - Items"],
    )
    def put(self, request, item_id: str):
        try:
            item = store_service.update_item(item_id, request.data)
            if not item:
                raise NotFoundError(safe_message="Item not found", status_code=404, code="not_found")
            return Response(ItemSerializer(item).data, status=status.HTTP_200_OK)
        except AppError:
            raise
        except Exception:
            raise DatabaseError(safe_message="An unexpected error occurred.", code="internal_error", status_code=500)

    @swagger_auto_schema(
        operation_summary="Delete an item",
        responses={
            204: "Item deleted",
            404: "Item not found",
            500: "Internal server error",
        },
        tags=["Store - Items"],
    )
    def delete(self, request, item_id: str):
        try:
            deleted = store_service.delete_item(item_id)
            if not deleted:
                raise NotFoundError(safe_message="Item not found", status_code=404, code="not_found")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AppError:
            raise
        except Exception:
            raise DatabaseError(safe_message="An unexpected error occurred while fetching items.", code="internal_error", status_code=500)

# Favorites
class FavoriteListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List user favorites",
        responses={200: FavoriteSerializer(many=True)},
        tags=["Store - Favorites"],
    )
    def get(self, request):
        try:
            favorites = store_service.list_favorites(user=request.user)
            serializer = FavoriteSerializer(favorites, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AppError:
            raise
        except Exception:
            raise DatabaseError(safe_message="An unexpected error occurred while fetching items.", code="internal_error", status_code=500)

    @swagger_auto_schema(
        operation_summary="Add an item to favorites",
        manual_parameters=[
            openapi.Parameter("item_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="UUID of item to favorite", required=True)
        ],
        responses={
            201: FavoriteSerializer(),
            400: "Missing item_id",
            404: "Item not found",
            500: "Internal server error",
        },
        tags=["Store - Favorites"],
    )
    def post(self, request):
        try:
            item_id = request.query_params.get("item_id")
            if not item_id:
                raise BadRequestError(safe_message="Item ID is required", status_code=400, code="bad_request")

            favorite = store_service.add_favorites(request.user, item_id)
            if not favorite:
                raise NotFoundError(safe_message="Item not found", status_code=404, code="not_found")

            return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)
        except AppError:
            raise
        except Exception:
            raise DatabaseError(safe_message="An unexpected error occurred.", code="internal_error", status_code=500)
class FavoriteRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Remove an item from favorites",
        manual_parameters=[
            openapi.Parameter("item_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
        ],
        responses={
            204: "Removed",
            400: "Missing item_id",
            404: "Item not found",
            500: "Internal server error",
        },
        tags=["Store - Favorites"],
    )
    def delete(self, request):
        try:
            item_id = request.query_params.get("item_id")
            if not item_id:
                raise BadRequestError(safe_message="Item ID is required", status_code=400, code="bad_request")

            removed = store_service.remove_favorite(request.user, item_id)
            if not removed:
                raise NotFoundError(safe_message="Item not found", status_code=404, code="not_found")

            return Response(status=status.HTTP_204_NO_CONTENT)
        except AppError:
            raise
        except Exception:
            raise DatabaseError(safe_message="An unexpected error occurred.", code="internal_error", status_code=500)

# Cart
class CartListAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List cart items for authenticated user",
        responses={200: CartItemSerializer(many=True)},
        tags=["Store - Cart"],
    )
    def get(self, request):
        try:
            cart = store_service.list_cart(request.user)
            return Response(CartItemSerializer(cart, many=True).data, status=status.HTTP_200_OK)
        except AppError:
            raise
        except Exception:
            raise DatabaseError(safe_message="An unexpected error occurred.", code="internal_error", status_code=500)

    @swagger_auto_schema(
        operation_summary="Add item to cart",
        request_body=CartAddSerializer,
        responses={
            201: CartItemSerializer(),
            400: "Invalid data",
            404: "Item not found",
            500: "Internal server error",
        },
        tags=["Store - Cart"],
    )
    def post(self, request):
        try:
            serializer = CartAddSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = cast(Dict[str, Any], serializer.validated_data)

            item_id = data.get("item_id")
            quantity = data.get("quantity", 1)

            if item_id is None:
                raise BadRequestError(safe_message="Item ID is required", status_code=400, code="bad_request")

            cart_item = store_service.add_to_cart(request.user, str(item_id), quantity)
            
            if not cart_item:
                raise NotFoundError(safe_message="Item not found", status_code=404, code="not_found")

            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
        except AppError:
            raise
        except Exception:
            raise DatabaseError(safe_message="An unexpected error occurred.", code="internal_error", status_code=500)

class CartRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Remove item from cart",
        manual_parameters=[
            openapi.Parameter("item_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
        ],
        responses={
            204: "Removed",
            400: "Missing item_id",
            404: "Item not found",
            500: "Internal server error",
        },
        tags=["Store - Cart"],
    )
    def delete(self, request):
        try:
            item_id = request.query_params.get("item_id")
            if not item_id:
                raise BadRequestError(safe_message="Item ID is required", status_code=400, code="bad_request")

            removed = store_service.remove_from_cart(request.user, item_id)
            if not removed:
                raise NotFoundError(safe_message="Item not found", status_code=404, code="not_found")

            return Response(status=status.HTTP_204_NO_CONTENT)
        except AppError:
            raise
        except Exception:
            raise DatabaseError(safe_message="An unexpected error occurred.", code="internal_error", status_code=500)

# Purchase
class PurchaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Purchase an item",
        operation_description="Complete a purchase for a single item. Sends shipping data and optional payment proof (file).",
        request_body=PurchaseRequestSerializer,
        responses={
            201: PurchaseSerializer(),
            400: "Invalid input or payment failed",
            401: "Unauthorized",
            404: "Item not found",
            500: "Internal server error",
        },
        tags=["Store - Purchase"],
    )
    def post(self, request):
        try:
            serializer = PurchaseSerializer(data=request.data)

            if not serializer.is_valid():
                raise BadRequestError(safe_message="Invalid data", extra=serializer.errors, status_code=400)

            data = serializer.validated_data
            if isinstance(data, dict):
                item_field = data.get("item")
            else:
                item_field = None

            item_id = getattr(item_field, "id", None) or (item_field if isinstance(item_field, str) else None)

            if not item_id:
                item_raw = request.data.get("item")
                if isinstance(item_raw, str):
                    item_id = item_raw

            if not item_id:
                raise BadRequestError(safe_message="item id is required", status_code=400, code="bad_request")

            if not isinstance(data, dict):
                data = {}

            shipping_data = {
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "city": data.get("city"),
                "country": data.get("country"),
                "street_address": data.get("street_address"),
                "house_number": data.get("house_number"),
                "phone": data.get("phone"),
                "email": data.get("email"),
            }

            payment_proof = data.get("payment_proof") or request.FILES.get("payment_proof")

            purchase = store_service.purchase_item(
                user=request.user,
                item_id=str(item_id),
                quantity=int(data.get("quantity", 1)),
                payment_method=str(data.get("payment_method")),
                payment_proof_file=payment_proof,
                shipping_data=shipping_data,
            )

            if not purchase:
                raise NotFoundError(safe_message="Item not found", status_code=404, code="not_found")

            return Response(PurchaseSerializer(purchase).data, status=status.HTTP_201_CREATED)

        except AppError:
            raise
        except Exception:
            raise DatabaseError(safe_message="An unexpected error occurred.", code="internal_error", status_code=500)