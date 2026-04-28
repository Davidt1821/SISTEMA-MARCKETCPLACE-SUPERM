from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Supermarket
from .serializers import SupermarketSerializer


class SupermarketViewSet(viewsets.ModelViewSet):
    queryset = Supermarket.objects.all()
    serializer_class = SupermarketSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'district', 'is_active']
    search_fields = ['name', 'cnpj', 'city', 'district']
    ordering_fields = ['name', 'city', 'created_at']

# Create your views here.
