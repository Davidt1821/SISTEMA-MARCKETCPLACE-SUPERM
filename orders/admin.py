from django.contrib import admin

from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name_snapshot', 'product_brand_snapshot', 'quantity', 'unit_price', 'subtotal']
    can_delete = False


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'changed_by', 'note', 'created_at']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'supermarket',
        'customer_name',
        'customer_phone',
        'fulfillment_method',
        'delivery_fee',
        'products_total',
        'final_total',
        'status',
        'created_at',
    ]
    list_filter = ['status', 'fulfillment_method', 'supermarket', 'created_at']
    search_fields = ['code', 'customer_name', 'customer_phone', 'supermarket__name']
    readonly_fields = ['code', 'total_amount', 'products_total', 'delivery_fee', 'final_total', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name_snapshot', 'quantity', 'unit_price', 'subtotal']
    search_fields = ['order__code', 'product_name_snapshot', 'product_brand_snapshot']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['new_status', 'created_at']
    search_fields = ['order__code', 'changed_by__username', 'note']
    readonly_fields = ['order', 'old_status', 'new_status', 'changed_by', 'note', 'created_at']
