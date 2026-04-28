from django.contrib import admin

from .models import Supermarket


@admin.register(Supermarket)
class SupermarketAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'cnpj',
        'city',
        'district',
        'delivery_available',
        'pickup_available',
        'default_delivery_fee',
        'is_active',
        'created_at',
    ]
    list_filter = ['city', 'district', 'delivery_available', 'pickup_available', 'is_active']
    search_fields = ['name', 'cnpj', 'city', 'district']
    fieldsets = [
        (None, {
            'fields': ['name', 'cnpj', 'phone', 'address', 'district', 'city', 'logo', 'is_active'],
        }),
        ('Entrega e retirada', {
            'fields': [
                'delivery_available',
                'pickup_available',
                'default_delivery_fee',
                'free_delivery_minimum',
                'delivery_notes',
            ],
        }),
    ]
