from rest_framework import serializers

from .models import ProductPrice


class ProductPriceSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_brand = serializers.CharField(source='product.brand', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    supermarket_name = serializers.CharField(source='supermarket.name', read_only=True)
    supermarket_city = serializers.CharField(source='supermarket.city', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    has_active_promotion = serializers.BooleanField(read_only=True)
    promotion_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, allow_null=True)
    promotion_start = serializers.DateField(read_only=True, allow_null=True)
    promotion_end = serializers.DateField(read_only=True, allow_null=True)

    class Meta:
        model = ProductPrice
        fields = [
            'id',
            'product',
            'product_name',
            'product_brand',
            'category_name',
            'supermarket',
            'supermarket_name',
            'supermarket_city',
            'current_price',
            'price',
            'old_price',
            'available',
            'has_active_promotion',
            'promotion_price',
            'promotion_start',
            'promotion_end',
            'updated_at',
        ]
        read_only_fields = ['updated_at']
