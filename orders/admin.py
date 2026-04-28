from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name_snapshot', 'product_brand_snapshot', 'quantity', 'unit_price', 'subtotal']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['code', 'supermarket', 'customer_name', 'customer_phone', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'supermarket', 'created_at']
    search_fields = ['code', 'customer_name', 'customer_phone', 'supermarket__name']
    readonly_fields = ['code', 'total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name_snapshot', 'quantity', 'unit_price', 'subtotal']
    search_fields = ['order__code', 'product_name_snapshot', 'product_brand_snapshot']
