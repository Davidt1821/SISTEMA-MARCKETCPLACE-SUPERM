from django.core.exceptions import ValidationError
from django.db import models

from products.models import Product
from supermarkets.models import Supermarket


class Promotion(models.Model):
    product = models.ForeignKey(Product, verbose_name='produto', on_delete=models.CASCADE, related_name='promotions')
    supermarket = models.ForeignKey(
        Supermarket,
        verbose_name='supermercado',
        on_delete=models.CASCADE,
        related_name='promotions',
    )
    promotional_price = models.DecimalField('preco promocional', max_digits=10, decimal_places=2)
    start_date = models.DateField('data de inicio')
    end_date = models.DateField('data de fim')
    description = models.TextField('descricao', blank=True)
    is_active = models.BooleanField('ativa', default=True)
    created_at = models.DateTimeField('criada em', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'promocao'
        verbose_name_plural = 'promocoes'

    def __str__(self):
        return f'{self.product} - {self.supermarket}'

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError({'end_date': 'A data final deve ser maior ou igual a data inicial.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
