from django.urls import path
from store.views import (
    ItemListCreateView, ItemDetailView,
    FavoriteListCreateView, FavoriteRemoveView,
    CartListAddView, CartRemoveView,
    PurchaseView,
)

urlpatterns = [
    path("items/", ItemListCreateView.as_view()),
    path("items/<uuid:item_id>/", ItemDetailView.as_view()),
    path("favorites/", FavoriteListCreateView.as_view()),
    path("favorites/remove/", FavoriteRemoveView.as_view()),
    path("cart/", CartListAddView.as_view()),
    path("cart/remove/", CartRemoveView.as_view()),
    path("purchase/", PurchaseView.as_view()),
]
