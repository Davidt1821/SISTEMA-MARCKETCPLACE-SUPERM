import uuid

from django.conf import settings
from django.db import models

from products.models import Product
from supermarkets.models import Supermarket


def generate_order_code():
    return uuid.uuid4().hex[:10].upper()


class Order(models.Model):
    FULFILLMENT_PICKUP = 'pickup'
    FULFILLMENT_DELIVERY = 'delivery'
    FULFILLMENT_ARRANGE = 'arrange'

    FULFILLMENT_CHOICES = [
        (FULFILLMENT_PICKUP, 'Retirada no supermercado'),
        (FULFILLMENT_DELIVERY, 'Entrega em casa'),
        (FULFILLMENT_ARRANGE, 'Combinar com o mercado'),
    ]

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
    internal_notes = models.TextField('observacoes internas', blank=True)
    fulfillment_method = models.CharField(
        'tipo de atendimento',
        max_length=20,
        choices=FULFILLMENT_CHOICES,
        default=FULFILLMENT_ARRANGE,
    )
    delivery_street = models.CharField('rua', max_length=150, blank=True)
    delivery_number = models.CharField('numero', max_length=30, blank=True)
    delivery_district = models.CharField('bairro', max_length=100, blank=True)
    delivery_city = models.CharField('cidade', max_length=100, blank=True)
    delivery_complement = models.CharField('complemento', max_length=150, blank=True)
    delivery_reference = models.CharField('referencia', max_length=150, blank=True)
    products_total = models.DecimalField('total dos produtos', max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField('taxa de entrega', max_digits=10, decimal_places=2, default=0)
    final_total = models.DecimalField('total final', max_digits=10, decimal_places=2, default=0)
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

    @property
    def delivery_address(self):
        parts = [
            self.delivery_street,
            self.delivery_number,
            self.delivery_district,
            self.delivery_city,
            self.delivery_complement,
            self.delivery_reference,
        ]
        return ', '.join(part for part in parts if part)


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


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, verbose_name='pedido', on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField('status anterior', max_length=20, choices=Order.STATUS_CHOICES, blank=True)
    new_status = models.CharField('novo status', max_length=20, choices=Order.STATUS_CHOICES)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='alterado por',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='order_status_changes',
    )
    note = models.TextField('observacao', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'historico de status'
        verbose_name_plural = 'historicos de status'

    def __str__(self):
        return f'{self.order.code}: {self.old_status} -> {self.new_status}'
