from rest_framework import serializers


class SearchProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    brand = serializers.CharField(allow_blank=True)
    category = serializers.CharField(source='category.name')
    barcode = serializers.CharField(allow_null=True)
    description = serializers.CharField(allow_blank=True)
    image = serializers.ImageField(allow_null=True)
    lowest_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    lowest_price_supermarket = serializers.CharField()
    lowest_price_city = serializers.CharField()
    has_active_promotion = serializers.BooleanField()


class ComparedStorePriceSerializer(serializers.Serializer):
    supermarket_id = serializers.IntegerField(source='supermarket.id')
    supermarket_name = serializers.CharField(source='supermarket.name')
    city = serializers.CharField(source='supermarket.city')
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='price')
    old_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    available = serializers.BooleanField()
    has_active_promotion = serializers.BooleanField()
    promotion_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    promotion_start = serializers.DateField(allow_null=True)
    promotion_end = serializers.DateField(allow_null=True)
    updated_at = serializers.DateTimeField()


class ProductComparisonSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(source='id')
    product_name = serializers.CharField(source='name')
    brand = serializers.CharField(allow_blank=True)
    category = serializers.CharField(source='category.name')
    barcode = serializers.CharField(allow_null=True)
    lowest_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    prices = ComparedStorePriceSerializer(many=True, source='comparison_prices')
