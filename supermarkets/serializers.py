from rest_framework import serializers

from .models import Supermarket


class SupermarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supermarket
        fields = [
            'id',
            'name',
            'cnpj',
            'phone',
            'address',
            'district',
            'city',
            'logo',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
