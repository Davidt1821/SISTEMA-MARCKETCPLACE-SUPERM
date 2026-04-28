from django.contrib import admin

from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = [
        'product',
        'supermarket',
        'promotional_price',
        'start_date',
        'end_date',
        'is_active',
    ]
    list_filter = ['is_active', 'start_date', 'end_date', 'supermarket']
    search_fields = ['product__name', 'product__brand', 'product__barcode', 'supermarket__name']

# Register your models here.
