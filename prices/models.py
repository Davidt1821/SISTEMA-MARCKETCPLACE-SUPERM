from django.db import models

from products.models import Product
from supermarkets.models import Supermarket


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, verbose_name='produto', on_delete=models.CASCADE, related_name='prices')
    supermarket = models.ForeignKey(
        Supermarket,
        verbose_name='supermercado',
        on_delete=models.CASCADE,
        related_name='prices',
    )
    price = models.DecimalField('preco', max_digits=10, decimal_places=2)
    old_price = models.DecimalField('preco antigo', max_digits=10, decimal_places=2, blank=True, null=True)
    available = models.BooleanField('disponivel', default=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['price']
        verbose_name = 'preco do produto'
        verbose_name_plural = 'precos dos produtos'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'supermarket'],
                name='unique_product_price_per_supermarket',
            )
        ]

    def __str__(self):
        return f'{self.product} em {self.supermarket}: R$ {self.price}'
