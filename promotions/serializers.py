from rest_framework import serializers

from .models import Promotion


class PromotionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_brand = serializers.CharField(source='product.brand', read_only=True)
    category_name = serializers.CharField(source='product.category.name', read_only=True)
    barcode = serializers.CharField(source='product.barcode', read_only=True)
    supermarket_name = serializers.CharField(source='supermarket.name', read_only=True)
    supermarket_city = serializers.CharField(source='supermarket.city', read_only=True)

    class Meta:
        model = Promotion
        fields = [
            'id',
            'product',
            'product_name',
            'product_brand',
            'category_name',
            'barcode',
            'supermarket',
            'supermarket_name',
            'supermarket_city',
            'promotional_price',
            'start_date',
            'end_date',
            'description',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def validate(self, attrs):
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({'end_date': 'A data final deve ser maior ou igual a data inicial.'})

        return attrs
