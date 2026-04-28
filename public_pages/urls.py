from django.urls import path

from orders.views import checkout
from . import shopping_list
from .views import ComparePageView, HomePageView, PromotionsPageView, SearchPageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('buscar/', SearchPageView.as_view(), name='public-search'),
    path('comparar/', ComparePageView.as_view(), name='public-compare'),
    path('promocoes/', PromotionsPageView.as_view(), name='public-promotions'),
    path('lista/', shopping_list.shopping_list_view, name='shopping-list'),
    path('lista/finalizar/<int:supermarket_id>/', checkout, name='shopping-list-checkout'),
    path('lista/adicionar/<int:product_id>/', shopping_list.add_to_list, name='shopping-list-add'),
    path('lista/remover/<int:product_id>/', shopping_list.remove_from_list, name='shopping-list-remove'),
    path('lista/aumentar/<int:product_id>/', shopping_list.increase_quantity, name='shopping-list-increase'),
    path('lista/diminuir/<int:product_id>/', shopping_list.decrease_quantity, name='shopping-list-decrease'),
    path('lista/limpar/', shopping_list.clear_list, name='shopping-list-clear'),
]
