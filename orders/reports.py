import csv
from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from accounts.panel import require_supermarket_profile
from products.models import Product
from promotions.models import Promotion
from supermarkets.models import Supermarket

from .models import Order, OrderItem


def default_date_range():
    today = timezone.localdate()
    start = today.replace(day=1)
    if start.month == 12:
        next_month = start.replace(year=start.year + 1, month=1)
    else:
        next_month = start.replace(month=start.month + 1)
    end = next_month - timedelta(days=1)
    return start, end


def parse_filters(request, include_supermarket=False):
    default_start, default_end = default_date_range()
    date_from = request.GET.get('date_from') or default_start.isoformat()
    date_to = request.GET.get('date_to') or default_end.isoformat()
    filters = {
        'date_from': date_from,
        'date_to': date_to,
        'status': (request.GET.get('status') or '').strip(),
        'fulfillment_method': (request.GET.get('fulfillment_method') or '').strip(),
    }
    if include_supermarket:
        filters['supermarket'] = (request.GET.get('supermarket') or '').strip()
    return filters


def apply_order_filters(queryset, filters):
    queryset = queryset.filter(created_at__date__gte=filters['date_from'], created_at__date__lte=filters['date_to'])
    if filters.get('status'):
        queryset = queryset.filter(status=filters['status'])
    if filters.get('fulfillment_method'):
        queryset = queryset.filter(fulfillment_method=filters['fulfillment_method'])
    if filters.get('supermarket'):
        queryset = queryset.filter(supermarket_id=filters['supermarket'])
    return queryset


def order_total_expression():
    return Coalesce('final_total', 'total_amount')


def build_report_context(orders):
    total_orders = orders.count()
    totals = orders.aggregate(
        total_estimated=Sum(order_total_expression()),
        avg_ticket=Avg(order_total_expression()),
    )
    items = OrderItem.objects.filter(order__in=orders)
    status_labels = dict(Order.STATUS_CHOICES)
    fulfillment_labels = dict(Order.FULFILLMENT_CHOICES)
    orders_by_status = [
        {'label': status_labels.get(row['status'], row['status']), 'total': row['total']}
        for row in orders.values('status').annotate(total=Count('id')).order_by('status')
    ]
    orders_by_fulfillment = [
        {'label': fulfillment_labels.get(row['fulfillment_method'], row['fulfillment_method']), 'total': row['total']}
        for row in orders.values('fulfillment_method').annotate(total=Count('id')).order_by('fulfillment_method')
    ]
    return {
        'total_orders': total_orders,
        'total_estimated': totals['total_estimated'] or 0,
        'avg_ticket': totals['avg_ticket'] or 0,
        'orders_by_status': orders_by_status,
        'top_products': (
            items.values('product_name_snapshot')
            .annotate(total_quantity=Sum('quantity'), total_revenue=Sum('subtotal'))
            .order_by('-total_quantity', 'product_name_snapshot')[:10]
        ),
        'top_categories': (
            items.values('product__category__name')
            .annotate(total_quantity=Sum('quantity'), total_revenue=Sum('subtotal'))
            .order_by('-total_quantity', 'product__category__name')[:10]
        ),
        'orders_by_fulfillment': orders_by_fulfillment,
        'delivery_districts': (
            orders.filter(fulfillment_method=Order.FULFILLMENT_DELIVERY)
            .exclude(delivery_district='')
            .values('delivery_district')
            .annotate(total=Count('id'))
            .order_by('-total', 'delivery_district')[:10]
        ),
        'recent_orders': orders.select_related('supermarket').order_by('-created_at')[:10],
    }


@login_required(login_url='market-login')
def market_reports(request):
    profile, response = require_supermarket_profile(request)
    if response:
        return response

    filters = parse_filters(request)
    orders = apply_order_filters(
        Order.objects.filter(supermarket=profile.supermarket).select_related('supermarket'),
        filters,
    )
    context = {
        'profile': profile,
        'filters': filters,
        'status_choices': Order.STATUS_CHOICES,
        'fulfillment_choices': Order.FULFILLMENT_CHOICES,
        **build_report_context(orders),
    }
    return render(request, 'market_panel/reports.html', context)


@login_required(login_url='market-login')
def export_market_orders(request):
    profile, response = require_supermarket_profile(request)
    if response:
        return response

    filters = parse_filters(request)
    orders = apply_order_filters(
        Order.objects.filter(supermarket=profile.supermarket).select_related('supermarket'),
        filters,
    ).order_by('-created_at')
    return export_orders_csv(orders, 'pedidos-supermercado.csv')


def staff_required(user):
    return user.is_active and user.is_staff


@user_passes_test(staff_required, login_url='/admin/login/')
def platform_reports(request):
    filters = parse_filters(request, include_supermarket=True)
    orders = apply_order_filters(Order.objects.select_related('supermarket'), filters)
    context = {
        'filters': filters,
        'status_choices': Order.STATUS_CHOICES,
        'fulfillment_choices': Order.FULFILLMENT_CHOICES,
        'supermarkets': Supermarket.objects.order_by('name'),
        'total_active_supermarkets': Supermarket.objects.filter(is_active=True).count(),
        'total_active_products': Product.objects.filter(is_active=True).count(),
        'active_promotions': active_promotions_count(),
        'supermarket_ranking_by_orders': (
            orders.values('supermarket__name')
            .annotate(total_orders=Count('id'))
            .order_by('-total_orders', 'supermarket__name')[:10]
        ),
        'supermarket_ranking_by_total': (
            orders.values('supermarket__name')
            .annotate(total_estimated=Sum(order_total_expression()))
            .order_by('-total_estimated', 'supermarket__name')[:10]
        ),
        **build_report_context(orders),
    }
    return render(request, 'platform/reports.html', context)


@user_passes_test(staff_required, login_url='/admin/login/')
def export_platform_orders(request):
    filters = parse_filters(request, include_supermarket=True)
    orders = apply_order_filters(Order.objects.select_related('supermarket'), filters).order_by('-created_at')
    return export_orders_csv(orders, 'pedidos-plataforma.csv')


def active_promotions_count():
    today = timezone.localdate()
    return Promotion.objects.filter(is_active=True, start_date__lte=today, end_date__gte=today).count()


def export_orders_csv(orders, filename):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow([
        'codigo',
        'data',
        'supermercado',
        'cliente',
        'telefone',
        'status',
        'tipo_atendimento',
        'bairro',
        'total_produtos',
        'taxa_entrega',
        'total_final',
    ])
    for order in orders:
        writer.writerow([
            order.code,
            order.created_at,
            order.supermarket.name,
            order.customer_name,
            order.customer_phone,
            order.get_status_display(),
            order.get_fulfillment_method_display(),
            order.delivery_district,
            order.products_total,
            order.delivery_fee,
            order.final_total or order.total_amount,
        ])
    return response
