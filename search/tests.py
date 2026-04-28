from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from prices.models import ProductPrice
from products.models import Category, Product
from promotions.models import Promotion
from supermarkets.models import Supermarket


class SearchApiTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Alimentos')
        self.product = Product.objects.create(
            name='Arroz Tipo 1 5kg',
            brand='Tio Joao',
            category=self.category,
            barcode='7891000100103',
            is_active=True,
        )
        self.supermarket = Supermarket.objects.create(
            name='Supermercado Central',
            cnpj='00000000000100',
            address='Rua A',
            district='Centro',
            city='Nova Serrana',
            is_active=True,
        )
        ProductPrice.objects.create(
            product=self.product,
            supermarket=self.supermarket,
            price=Decimal('24.90'),
            old_price=Decimal('27.90'),
            available=True,
        )
        Promotion.objects.create(
            product=self.product,
            supermarket=self.supermarket,
            promotional_price=Decimal('22.90'),
            start_date=date(2026, 4, 20),
            end_date=date(2026, 5, 20),
            is_active=True,
        )

    @patch('django.utils.timezone.localdate')
    def test_search_returns_matching_products(self, mocked_localdate):
        mocked_localdate.return_value = date(2026, 4, 27)
        response = self.client.get(reverse('search-products'), {'q': 'arroz'})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['lowest_price'], '22.90')
        self.assertEqual(payload[0]['lowest_price_supermarket'], 'Supermercado Central')

    @patch('django.utils.timezone.localdate')
    def test_compare_returns_prices_ordered_by_effective_price(self, mocked_localdate):
        mocked_localdate.return_value = date(2026, 4, 27)
        response = self.client.get(reverse('compare-product-prices'), {'q': 'arroz'})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['lowest_price'], '22.90')
        self.assertEqual(payload[0]['prices'][0]['current_price'], '22.90')
        self.assertTrue(payload[0]['prices'][0]['has_active_promotion'])
