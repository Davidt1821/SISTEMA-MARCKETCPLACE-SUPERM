from django.urls import path

from orders import reports
from . import panel

urlpatterns = [
    path('login/', panel.supermarket_login, name='market-login'),
    path('logout/', panel.supermarket_logout, name='market-logout'),
    path('dashboard/', panel.dashboard, name='market-dashboard'),
    path('relatorios/', reports.market_reports, name='market-reports'),
    path('relatorios/exportar-pedidos/', reports.export_market_orders, name='market-reports-export-orders'),
    path('pedidos/', panel.order_list, name='market-orders'),
    path('pedidos/<int:pk>/', panel.order_detail, name='market-order-detail'),
    path('precos/', panel.price_list, name='market-prices'),
    path('precos/editar/<int:pk>/', panel.price_edit, name='market-price-edit'),
    path('promocoes/', panel.promotion_list, name='market-promotions'),
    path('promocoes/nova/', panel.promotion_create, name='market-promotion-create'),
    path('promocoes/editar/<int:pk>/', panel.promotion_edit, name='market-promotion-edit'),
    path('importar-csv/', panel.import_csv, name='market-import-csv'),
]
