from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .filters import PromotionFilter
from .models import Promotion
from .serializers import PromotionSerializer


class PromotionViewSet(viewsets.ModelViewSet):
    serializer_class = PromotionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PromotionFilter
    search_fields = ['product__name', 'product__brand', 'product__barcode', 'supermarket__name']
    ordering_fields = ['promotional_price', 'start_date', 'end_date', 'created_at']

    def get_queryset(self):
        today = timezone.localdate()
        return (
            Promotion.objects.select_related('product', 'product__category', 'supermarket')
            .filter(
                is_active=True,
                start_date__lte=today,
                end_date__gte=today,
            )
            .order_by('promotional_price', 'product__name')
        )
