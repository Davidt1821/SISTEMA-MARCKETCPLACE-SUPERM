from django.urls import path

from . import customer_views

urlpatterns = [
    path('cadastro/', customer_views.customer_register, name='customer-register'),
    path('login/', customer_views.customer_login, name='customer-login'),
    path('logout/', customer_views.customer_logout, name='customer-logout'),
    path('painel/', customer_views.customer_dashboard, name='customer-dashboard'),
    path('perfil/', customer_views.customer_profile, name='customer-profile'),
    path('pedidos/', customer_views.customer_orders, name='customer-orders'),
    path('pedidos/<str:code>/', customer_views.customer_order_detail, name='customer-order-detail'),
]
