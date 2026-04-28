import django_filters

from .models import ProductPrice


class ProductPriceFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='product__name', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='product__category__name', lookup_expr='icontains')
    brand = django_filters.CharFilter(field_name='product__brand', lookup_expr='icontains')
    supermarket = django_filters.CharFilter(field_name='supermarket__name', lookup_expr='icontains')
    city = django_filters.CharFilter(field_name='supermarket__city', lookup_expr='icontains')

    class Meta:
        model = ProductPrice
        fields = ['product', 'supermarket', 'available']
