from django.db.models import BooleanField, Case, DecimalField, Exists, OuterRef, Prefetch, Q, Subquery, Value, When
from django.db.models.functions import Coalesce
from django.utils import timezone

from prices.models import ProductPrice
from products.models import Product
from promotions.models import Promotion


def parse_available_param(raw_value, default=True):
    if raw_value is None:
        return default

    normalized = raw_value.strip().lower()
    truthy = {'true', '1', 'sim', 's', 'yes'}
    falsy = {'false', '0', 'nao', 'n', 'no'}

    if normalized in truthy:
        return True
    if normalized in falsy:
        return False
    return default


def _clone_params(params):
    if hasattr(params, 'items'):
        return {key: params.get(key) for key in params.keys()}
    return dict(params)


def _params_with_available(params, available_value):
    cloned = _clone_params(params)
    cloned['available'] = available_value
    return cloned


def active_promotions_subquery():
    today = timezone.localdate()
    return Promotion.objects.filter(
        product=OuterRef('product'),
        supermarket=OuterRef('supermarket'),
        is_active=True,
        start_date__lte=today,
        end_date__gte=today,
    ).order_by('promotional_price', '-created_at')


def annotated_prices_queryset():
    active_promotions = active_promotions_subquery()
    return ProductPrice.objects.select_related('product', 'product__category', 'supermarket').annotate(
        promotion_price=Subquery(active_promotions.values('promotional_price')[:1]),
        promotion_start=Subquery(active_promotions.values('start_date')[:1]),
        promotion_end=Subquery(active_promotions.values('end_date')[:1]),
    ).annotate(
        current_price=Coalesce('promotion_price', 'price', output_field=DecimalField(max_digits=10, decimal_places=2)),
        has_active_promotion=Case(
            When(promotion_price__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        ),
    )


def apply_price_filters(queryset, params, default_available=True):
    available = parse_available_param(params.get('available'), default=default_available)
    queryset = queryset.filter(product__is_active=True, supermarket__is_active=True)
    if available is not None:
        queryset = queryset.filter(available=available)

    query = (params.get('q') or '').strip()
    category = (params.get('category') or '').strip()
    brand = (params.get('brand') or '').strip()
    city = (params.get('city') or '').strip()
    supermarket = (params.get('supermarket') or '').strip()
    barcode = (params.get('barcode') or '').strip()

    if query:
        queryset = queryset.filter(
            Q(product__name__icontains=query)
            | Q(product__brand__icontains=query)
            | Q(product__barcode__iexact=query)
            | Q(product__category__name__icontains=query)
        )
    if category:
        queryset = queryset.filter(product__category__name__icontains=category)
    if brand:
        queryset = queryset.filter(product__brand__icontains=brand)
    if city:
        queryset = queryset.filter(supermarket__city__icontains=city)
    if supermarket:
        queryset = queryset.filter(supermarket__name__icontains=supermarket)
    if barcode:
        queryset = queryset.filter(product__barcode__iexact=barcode)

    return queryset


def search_products_queryset(params, default_available=True):
    filtered_prices = apply_price_filters(annotated_prices_queryset(), params, default_available=default_available)
    lowest_price_subquery = filtered_prices.filter(product=OuterRef('pk')).order_by('current_price', 'supermarket__name')
    available_prices = apply_price_filters(
        annotated_prices_queryset(),
        _params_with_available(params, 'true'),
        default_available=True,
    )
    lowest_available_subquery = available_prices.filter(product=OuterRef('pk')).order_by('current_price', 'supermarket__name')

    return (
        Product.objects.select_related('category')
        .filter(is_active=True)
        .annotate(
            has_matching_price=Exists(filtered_prices.filter(product=OuterRef('pk'))),
            has_available_offer=Exists(available_prices.filter(product=OuterRef('pk'))),
            lowest_available_price=Subquery(lowest_available_subquery.values('current_price')[:1]),
            lowest_any_price=Subquery(lowest_price_subquery.values('current_price')[:1]),
            lowest_available_supermarket=Subquery(lowest_available_subquery.values('supermarket__name')[:1]),
            lowest_any_supermarket=Subquery(lowest_price_subquery.values('supermarket__name')[:1]),
            lowest_available_city=Subquery(lowest_available_subquery.values('supermarket__city')[:1]),
            lowest_any_city=Subquery(lowest_price_subquery.values('supermarket__city')[:1]),
            has_active_promotion=Exists(
                filtered_prices.filter(product=OuterRef('pk'), promotion_price__isnull=False)
            ),
        )
        .annotate(
            lowest_price=Coalesce('lowest_available_price', 'lowest_any_price'),
            lowest_price_supermarket=Coalesce('lowest_available_supermarket', 'lowest_any_supermarket'),
            lowest_price_city=Coalesce('lowest_available_city', 'lowest_any_city'),
        )
        .filter(has_matching_price=True)
        .order_by('lowest_price', 'name')
    )


def comparison_products_queryset(query, params=None, default_available=True):
    params = _clone_params(params or {})
    params['q'] = query
    filtered_prices = apply_price_filters(annotated_prices_queryset(), params, default_available=default_available)

    products = (
        Product.objects.select_related('category')
        .filter(is_active=True, prices__in=filtered_prices)
        .distinct()
        .order_by('name', 'brand')
        .prefetch_related(
            Prefetch(
                'prices',
                queryset=filtered_prices.order_by('current_price', 'supermarket__name'),
                to_attr='comparison_prices',
            )
        )
    )

    results = []
    for product in products:
        prices = [price for price in getattr(product, 'comparison_prices', []) if price.product_id == product.id]
        if not prices:
            continue

        best_price = next((price for price in prices if price.available), prices[0])
        for price in prices:
            price.is_best_price = price.pk == best_price.pk

        product.comparison_prices = prices
        product.lowest_price = best_price.current_price
        results.append(product)

    return results


def active_promotions_queryset():
    today = timezone.localdate()
    regular_price_subquery = ProductPrice.objects.filter(
        product=OuterRef('product'),
        supermarket=OuterRef('supermarket'),
    ).values('price')[:1]

    return (
        Promotion.objects.select_related('product', 'product__category', 'supermarket')
        .filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )
        .annotate(
            regular_price=Subquery(regular_price_subquery, output_field=DecimalField(max_digits=10, decimal_places=2)),
        )
        .order_by('promotional_price', 'product__name')
    )
