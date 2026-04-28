import uuid

from django.db import models

from products.models import Product
from supermarkets.models import Supermarket


def generate_order_code():
    return uuid.uuid4().hex[:10].upper()


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_REVIEWING = 'reviewing'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_FINISHED = 'finished'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_REVIEWING, 'Em analise'),
        (STATUS_ACCEPTED, 'Aceito'),
        (STATUS_REJECTED, 'Recusado'),
        (STATUS_FINISHED, 'Finalizado'),
    ]

    code = models.CharField('codigo', max_length=12, unique=True, default=generate_order_code, editable=False)
    supermarket = models.ForeignKey(
        Supermarket,
        verbose_name='supermercado',
        on_delete=models.PROTECT,
        related_name='orders',
    )
    customer_name = models.CharField('nome do cliente', max_length=150)
    customer_phone = models.CharField('telefone do cliente', max_length=30)
    customer_address = models.CharField('endereco do cliente', max_length=255, blank=True)
    notes = models.TextField('observacoes', blank=True)
    status = models.CharField('status', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total_amount = models.DecimalField('valor total', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'

    def __str__(self):
        return f'Pedido {self.code} - {self.supermarket}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='pedido', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, verbose_name='produto', on_delete=models.PROTECT, related_name='order_items')
    product_name_snapshot = models.CharField('nome do produto', max_length=150)
    product_brand_snapshot = models.CharField('marca do produto', max_length=100, blank=True)
    quantity = models.PositiveIntegerField('quantidade')
    unit_price = models.DecimalField('preco unitario', max_digits=10, decimal_places=2)
    subtotal = models.DecimalField('subtotal', max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['product_name_snapshot']
        verbose_name = 'item do pedido'
        verbose_name_plural = 'itens do pedido'

    def __str__(self):
        return f'{self.product_name_snapshot} x{self.quantity}'
