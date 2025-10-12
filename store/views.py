from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from store.services.store_service import StoreService
from store.serializers import (
    ItemSerializer, ItemCreateUpdateSerializer,
    FavoriteSerializer, CartItemSerializer, 
    CartAddSerializer, PurchaseSerializer
)
from store.models import Item, Favorite, CartItem, Purchase
from store.helpers.errors.error import DatabaseError, NotFoundError, UnauthorizedError, BadRequestError


store_service = StoreService()
class ItemListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        responses={200: ItemSerializer(many=True)},
        operation_summary="Listar todos os itens disponíveis"
    )
    def get(self, request):
        items = store_service.list_item()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=ItemCreateUpdateSerializer,
        responses={201: ItemSerializer()},
        operation_summary="Criar um novo item"
    )
    def post(self, request):
        serializer = ItemCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = store_service.create_item(serializer.validated_data)
        return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)

class ItemDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        responses={200: ItemSerializer()},
        operation_summary="Obter detalhes de um item"
    )
    def get(self, request, item_id: str):
        item = store_service.get_items(item_id)
        if not item:
            raise NotFoundError("Item não encontrado")
        return Response(ItemSerializer(item).data)

    @swagger_auto_schema(
        request_body=ItemCreateUpdateSerializer,
        responses={200: ItemSerializer()},
        operation_summary="Atualizar informações de um item"
    )
    def put(self, request, item_id: str):
        item = store_service.update_item(item_id, request.data)
        if not item:
            raise NotFoundError("Item não encontrado")
        return Response(ItemSerializer(item).data)

    @swagger_auto_schema(
        operation_summary="Remover um item"
    )
    def delete(self, request, item_id: str):
        deleted = store_service.delete_item(item_id)
        if not deleted:
            raise NotFoundError("Item não encontrado")
        return Response(status=status.HTTP_204_NO_CONTENT)

class FavoriteListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: FavoriteSerializer(many=True)},
        operation_summary="Listar todos os favoritos do usuário"
    )
    def get(self, request):
        favorites = store_service.list_favorites(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("item_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
        ],
        responses={201: FavoriteSerializer()},
        operation_summary="Adicionar um item aos favoritos"
    )
    def post(self, request):
        item_id = request.query_params.get("item_id")
        if not item_id:
            raise BadRequestError("Item ID é obrigatório")

        favorite = store_service.add_favorites(request.user, item_id)
        if not favorite:
            raise NotFoundError("Item não encontrado")

        return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)

class FavoriteRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("item_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
        ],
        operation_summary="Remover um item dos favoritos"
    )
    def delete(self, request):
        item_id = request.query_params.get("item_id")
        if not item_id:
            raise BadRequestError("Item ID é obrigatório")

        removed = store_service.remove_favorite(request.user, item_id)
        if not removed:
            raise NotFoundError("Item não encontrado")
        return Response(status=status.HTTP_204_NO_CONTENT)

class CartListAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: CartItemSerializer(many=True)},
        operation_summary="Listar itens no carrinho"
    )
    def get(self, request):
        cart = store_service.list_cart(request.user)
        return Response(CartItemSerializer(cart, many=True).data)

    @swagger_auto_schema(
        request_body=CartAddSerializer,
        responses={201: CartItemSerializer()},
        operation_summary="Adicionar um item ao carrinho"
    )
    def post(self, request):
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id = serializer.validated_data["item_id"]
        quantity = serializer.validated_data["quatity"]

        cart_item = store_service.add_to_cart(request.user, item_id, quantity)
        return Response(CratItemerializer(cart_item).data, status=status.HTTP_201_CREATED)

class CartRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("item_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
        ],
        operation_summary="Remover um item do carrinho"
    )
    def delete(self, request):
        item_id = request.query_params.get("item_id")
        if not item_id:
            raise BadRequestError("Item ID é obrigatório")

        removed = store_service.remove_from_cart(request.user, item_id)
        if not removed:
            raise NotFoundError("Item não encontrado")
        return Response(status=status.HTTP_204_NO_CONTENT)

class PurchaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=PurchaseSerializer,
        responses={201: PurchaseSerializer()},
        operation_summary="Efetuar a compra de um item"
    )
    def post(self, request):
        serializer = PurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        purchase = store_service.purchase_item(
            user=request.user,
            item_id=data["item"].id,
            quantity=data["quantity"],
            payment_method=data["payment_method"],
            payment_proof_file=data.get("payment_proof"),
            shipping_data=data,
        )

        return Response(PurchaseSerializer(purchase).data, status=status.HTTP_201_CREATED)
