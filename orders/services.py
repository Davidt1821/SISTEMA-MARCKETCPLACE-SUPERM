from decimal import Decimal

from django.db import transaction

from products.models import Product
from search.querysets import annotated_prices_queryset

from .models import Order, OrderItem


def build_order_preview(session_items, supermarket):
    product_ids = [int(product_id) for product_id in session_items.keys()]
    products = Product.objects.filter(id__in=product_ids, is_active=True).select_related('category')
    product_map = {product.id: product for product in products}
    prices = (
        annotated_prices_queryset()
        .filter(product_id__in=product_ids, supermarket=supermarket, available=True)
        .order_by('product__name')
    )
    price_map = {price.product_id: price for price in prices}

    available_items = []
    missing_items = []
    total = Decimal('0.00')

    for product_id in product_ids:
        product = product_map.get(product_id)
        if not product:
            continue

        quantity = int(session_items[str(product_id)])
        price = price_map.get(product_id)
        if not price:
            missing_items.append({
                'product': product,
                'quantity': quantity,
            })
            continue

        subtotal = price.current_price * quantity
        available_items.append({
            'product': product,
            'quantity': quantity,
            'unit_price': price.current_price,
            'subtotal': subtotal,
            'has_active_promotion': price.has_active_promotion,
        })
        total += subtotal

    return {
        'available_items': available_items,
        'missing_items': missing_items,
        'total': total,
    }


@transaction.atomic
def create_order_from_preview(supermarket, form_data, preview):
    order = Order.objects.create(
        supermarket=supermarket,
        customer_name=form_data['customer_name'],
        customer_phone=form_data['customer_phone'],
        customer_address=form_data.get('customer_address') or '',
        notes=form_data.get('notes') or '',
        total_amount=preview['total'],
    )

    items = []
    for item in preview['available_items']:
        product = item['product']
        items.append(OrderItem(
            order=order,
            product=product,
            product_name_snapshot=product.name,
            product_brand_snapshot=product.brand,
            quantity=item['quantity'],
            unit_price=item['unit_price'],
            subtotal=item['subtotal'],
        ))

    OrderItem.objects.bulk_create(items)
    return order
