from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from prices.serializers import ProductPriceSerializer
from search.querysets import annotated_prices_queryset

from .filters import ProductFilter
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').prefetch_related('prices__supermarket').distinct()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'brand', 'barcode', 'description']
    ordering_fields = ['name', 'brand', 'created_at']

    @action(detail=True, methods=['get'])
    def prices(self, request, pk=None):
        product = self.get_object()
        queryset = annotated_prices_queryset().filter(product=product).order_by('current_price', 'supermarket__name')
        serializer = ProductPriceSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
