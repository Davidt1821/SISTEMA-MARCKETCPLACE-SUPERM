from django.contrib import admin

from .models import ProductPrice


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'supermarket', 'price', 'old_price', 'available', 'updated_at']
    list_filter = ['available', 'supermarket__city', 'supermarket']
    search_fields = ['product__name', 'product__brand', 'product__barcode', 'supermarket__name']

# Register your models here.
