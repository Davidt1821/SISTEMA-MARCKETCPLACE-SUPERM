from django.urls import path

from . import views

urlpatterns = [
    path('pedido/<str:code>/', views.order_detail, name='order-detail-public'),
    path('pedido/<str:code>/comprovante/', views.order_receipt, name='order-receipt-public'),
]
