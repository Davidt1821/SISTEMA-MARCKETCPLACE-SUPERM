import django_filters

from .models import Promotion


class PromotionFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name='supermarket__city', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='product__category__name', lookup_expr='icontains')
    supermarket = django_filters.CharFilter(field_name='supermarket__name', lookup_expr='icontains')
    brand = django_filters.CharFilter(field_name='product__brand', lookup_expr='icontains')
    barcode = django_filters.CharFilter(field_name='product__barcode', lookup_expr='iexact')

    class Meta:
        model = Promotion
        fields = ['city', 'category', 'supermarket', 'brand', 'barcode']
