from django.urls import path
from store.views import (
    ItemListCreateView, ItemDetailView,
    FavoriteListCreateView, FavoriteRemoveView,
    CartListAddView, CartRemoveView,
    PurchaseView,
    FeaturedItemView
)

urlpatterns = [
    path("store/items/", ItemListCreateView.as_view()),
    path("store/featured/", FeaturedItemView.as_view(), name="featured-products"),
    path("store/items/<uuid:item_id>/", ItemDetailView.as_view()),
    path("store/favorites/", FavoriteListCreateView.as_view()),
    path("store/favorites/remove/", FavoriteRemoveView.as_view()),
    path("store/cart/", CartListAddView.as_view()),
    path("store/cart/remove/", CartRemoveView.as_view()),
    path("store/purchase/", PurchaseView.as_view()),
]
