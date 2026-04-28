from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from search.querysets import annotated_prices_queryset

from .filters import ProductPriceFilter
from .serializers import ProductPriceSerializer


class ProductPriceViewSet(viewsets.ModelViewSet):
    serializer_class = ProductPriceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductPriceFilter
    search_fields = ['product__name', 'product__barcode', 'product__brand', 'supermarket__name']
    ordering_fields = ['price', 'updated_at']

    def get_queryset(self):
        return annotated_prices_queryset()
