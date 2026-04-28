import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    brand = django_filters.CharFilter(field_name='brand', lookup_expr='icontains')
    barcode = django_filters.CharFilter(field_name='barcode', lookup_expr='iexact')
    supermarket = django_filters.CharFilter(field_name='prices__supermarket__name', lookup_expr='icontains')
    city = django_filters.CharFilter(field_name='prices__supermarket__city', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['category', 'brand', 'barcode', 'is_active']
