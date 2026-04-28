from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from prices.models import ProductPrice
from products.models import Category, Product
from promotions.models import Promotion
from supermarkets.models import Supermarket


class PublicPagesTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Alimentos')
        product = Product.objects.create(
            name='Arroz Tipo 1 5kg',
            brand='Tio Joao',
            category=category,
            barcode='7891000100103',
            is_active=True,
        )
        supermarket = Supermarket.objects.create(
            name='Supermercado Central',
            cnpj='00000000000100',
            address='Rua A',
            district='Centro',
            city='Nova Serrana',
            is_active=True,
        )
        ProductPrice.objects.create(
            product=product,
            supermarket=supermarket,
            price=Decimal('24.90'),
            old_price=Decimal('27.90'),
            available=True,
        )
        Promotion.objects.create(
            product=product,
            supermarket=supermarket,
            promotional_price=Decimal('22.90'),
            start_date=date(2026, 4, 20),
            end_date=date(2026, 5, 20),
            is_active=True,
        )

    @patch('django.utils.timezone.localdate')
    def test_public_pages_render(self, mocked_localdate):
        mocked_localdate.return_value = date(2026, 4, 27)

        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        self.assertEqual(self.client.get(reverse('public-search'), {'q': 'arroz'}).status_code, 200)
        self.assertEqual(self.client.get(reverse('public-compare'), {'q': 'arroz'}).status_code, 200)
        self.assertEqual(self.client.get(reverse('public-promotions')).status_code, 200)
