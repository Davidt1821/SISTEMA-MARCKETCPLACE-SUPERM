from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product
from search.querysets import annotated_prices_queryset


SESSION_KEY = 'shopping_list'


def get_session_list(request):
    raw_items = request.session.get(SESSION_KEY, {})
    normalized = {}

    for product_id, quantity in raw_items.items():
        try:
            product_id = str(int(product_id))
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue
        if quantity > 0:
            normalized[product_id] = quantity

    if normalized != raw_items:
        request.session[SESSION_KEY] = normalized
        request.session.modified = True

    return normalized


def save_session_list(request, items):
    request.session[SESSION_KEY] = {str(product_id): max(1, int(quantity)) for product_id, quantity in items.items()}
    request.session.modified = True


def shopping_list_view(request):
    session_items = get_session_list(request)
    product_ids = [int(product_id) for product_id in session_items.keys()]
    products = Product.objects.filter(id__in=product_ids, is_active=True).select_related('category').order_by('name')
    product_map = {product.id: product for product in products}

    list_items = []
    for product_id in product_ids:
        product = product_map.get(product_id)
        if not product:
            continue
        quantity = session_items[str(product_id)]
        lowest_price = (
            annotated_prices_queryset()
            .filter(product=product, available=True, supermarket__is_active=True)
            .order_by('current_price', 'supermarket__name')
            .first()
        )
        list_items.append({
            'product': product,
            'quantity': quantity,
            'lowest_price': lowest_price,
            'estimated_subtotal': lowest_price.current_price * quantity if lowest_price else None,
        })

    comparisons = build_supermarket_comparisons(list_items)

    return render(request, 'public_pages/shopping_list.html', {
        'items': list_items,
        'comparisons': comparisons,
    })


@require_POST
def add_to_list(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    items = get_session_list(request)
    key = str(product.id)
    items[key] = items.get(key, 0) + 1
    save_session_list(request, items)
    messages.success(request, f'{product.name} foi adicionado a lista.')
    return redirect(request.META.get('HTTP_REFERER') or 'shopping-list')


@require_POST
def remove_from_list(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    items = get_session_list(request)
    items.pop(str(product.id), None)
    save_session_list(request, items)
    messages.success(request, f'{product.name} foi removido da lista.')
    return redirect('shopping-list')


@require_POST
def increase_quantity(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    items = get_session_list(request)
    key = str(product.id)
    items[key] = items.get(key, 0) + 1
    save_session_list(request, items)
    return redirect('shopping-list')


@require_POST
def decrease_quantity(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    items = get_session_list(request)
    key = str(product.id)
    current_quantity = items.get(key, 0)

    if current_quantity <= 1:
        items.pop(key, None)
    else:
        items[key] = current_quantity - 1

    save_session_list(request, items)
    return redirect('shopping-list')


@require_POST
def clear_list(request):
    request.session[SESSION_KEY] = {}
    request.session.modified = True
    messages.success(request, 'Lista de compras limpa.')
    return redirect('shopping-list')


def build_supermarket_comparisons(list_items):
    if not list_items:
        return []

    product_ids = [item['product'].id for item in list_items]
    quantities = {item['product'].id: item['quantity'] for item in list_items}
    product_names = {item['product'].id: item['product'].name for item in list_items}
    prices = (
        annotated_prices_queryset()
        .filter(product_id__in=product_ids, available=True, supermarket__is_active=True)
        .order_by('supermarket__name', 'product__name')
    )

    supermarket_map = {}
    for price in prices:
        supermarket_id = price.supermarket_id
        if supermarket_id not in supermarket_map:
            supermarket_map[supermarket_id] = {
                'supermarket': price.supermarket,
                'available_items': [],
                'missing_items': set(product_ids),
                'total': Decimal('0.00'),
                'has_all_items': False,
                'is_best_total': False,
            }

        quantity = quantities[price.product_id]
        subtotal = price.current_price * quantity
        row = supermarket_map[supermarket_id]
        row['available_items'].append({
            'product': price.product,
            'quantity': quantity,
            'unit_price': price.current_price,
            'subtotal': subtotal,
            'has_active_promotion': price.has_active_promotion,
        })
        row['missing_items'].discard(price.product_id)
        row['total'] += subtotal

    comparisons = []
    for row in supermarket_map.values():
        row['missing_items'] = [product_names[product_id] for product_id in row['missing_items']]
        row['has_all_items'] = not row['missing_items']
        comparisons.append(row)

    comparisons.sort(key=lambda item: (item['total'], not item['has_all_items'], item['supermarket'].name))
    complete_comparisons = [item for item in comparisons if item['has_all_items']]
    if complete_comparisons:
        complete_comparisons[0]['is_best_total'] = True

    return comparisons
