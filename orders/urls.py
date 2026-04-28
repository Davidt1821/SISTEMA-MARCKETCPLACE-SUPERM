from django.urls import path

from . import views

urlpatterns = [
    path('pedido/<str:code>/', views.order_detail, name='order-detail-public'),
]
