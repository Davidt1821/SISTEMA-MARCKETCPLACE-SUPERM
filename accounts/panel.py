from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from prices.models import ProductPrice
from products.services.csv_importer import CSVImportError, import_products_csv_for_supermarket
from promotions.models import Promotion
from orders.models import Order, OrderStatusHistory

from .forms import OrderInternalNotesForm, OrderStatusForm, PriceForm, PromotionForm, SupermarketCSVImportForm
from .models import SupermarketUser


def supermarket_login(request):
    if request.user.is_authenticated:
        profile = get_supermarket_profile(request.user)
        if profile:
            return redirect('market-dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('market-dashboard')

    return render(request, 'market_panel/login.html', {'form': form})


def supermarket_logout(request):
    logout(request)
    return redirect('market-login')


def get_supermarket_profile(user):
    return (
        SupermarketUser.objects.select_related('supermarket', 'user')
        .filter(user=user, is_active=True, supermarket__is_active=True)
        .first()
    )


def require_supermarket_profile(request):
    profile = get_supermarket_profile(request.user)
    if not profile:
        return None, render(request, 'market_panel/no_access.html', status=403)
    return profile, None


@login_required(login_url='market-login')
def dashboard(request):
    profile, response = require_supermarket_profile(request)
    if response:
        return response

    supermarket = profile.supermarket
    today = timezone.localdate()
    prices = ProductPrice.objects.filter(supermarket=supermarket)
    context = {
        'profile': profile,
        'supermarket': supermarket,
        'total_products': prices.values('product').distinct().count(),
        'total_available_prices': prices.filter(available=True).count(),
        'total_active_promotions': Promotion.objects.filter(
            supermarket=supermarket,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        ).count(),
        'latest_prices': prices.select_related('product', 'product__category').order_by('-updated_at')[:8],
    }
    return render(request, 'market_panel/dashboard.html', context)


@login_required(login_url='market-login')
def price_list(request):
    profile, response = require_supermarket_profile(request)
    if response:
        return response

    prices = (
        ProductPrice.objects.filter(supermarket=profile.supermarket)
        .select_related('product', 'product__category')
        .order_by('product__name', 'product__brand')
    )
    return render(request, 'market_panel/price_list.html', {'profile': profile, 'prices': prices})


@login_required(login_url='market-login')
def price_edit(request, pk):
    profile, response = require_supermarket_profile(request)
    if response:
        return response

    price = get_object_or_404(
        ProductPrice.objects.select_related('product', 'product__category', 'supermarket'),
        pk=pk,
        supermarket=profile.supermarket,
    )
    form = PriceForm(request.POST or None, instance=price)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Preco atualizado com sucesso.')
        return redirect('market-prices')

    return render(request, 'market_panel/price_form.html', {'profile': profile, 'form': form, 'price': price})


@login_required(login_url='market-login')
def promotion_list(request):
    profile, response = require_supermarket_profile(request)
    if response:
        return response

    promotions = (
        Promotion.objects.filter(supermarket=profile.supermarket)
        .select_related('product', 'product__category')
        .order_by('-created_at')
    )
    return render(request, 'market_panel/promotion_list.html', {'profile': profile, 'promotions': promotions})


@login_required(login_url='market-login')
def promotion_create(request):
    profile, response = require_supermarket_profile(request)
    if response:
        return response

    form = PromotionForm(request.POST or None, supermarket=profile.supermarket)
    if request.method == 'POST' and form.is_valid():
        promotion = form.save(commit=False)
        promotion.supermarket = profile.supermarket
        promotion.save()
        messages.success(request, 'Promocao criada com sucesso.')
        return redirect('market-promotions')

    return render(request, 'market_panel/promotion_form.html', {'profile': profile, 'form': form, 'title': 'Nova promocao'})


@login_required(login_url='market-login')
def promotion_edit(request, pk):
    profile, response = require_supermarket_profile(request)
    if response:
        return response

    promotion = get_object_or_404(
        Promotion.objects.select_related('product', 'product__category', 'supermarket'),
        pk=pk,
        supermarket=profile.supermarket,
    )
    form = PromotionForm(request.POST or None, instance=promotion, supermarket=profile.supermarket)
    if request.method == 'POST' and form.is_valid():
        promotion = form.save(commit=False)
        promotion.supermarket = profile.supermarket
        promotion.save()
        messages.success(request, 'Promocao atualizada com sucesso.')
        return redirect('market-promotions')

    return render(request, 'market_panel/promotion_form.html', {'profile': profile, 'form': form, 'title': 'Editar promocao'})


@login_required(login_url='market-login')
def import_csv(request):
    profile, response = require_supermarket_profile(request)
    if response:
        return response

    form = SupermarketCSVImportForm(request.POST or None, request.FILES or None)
    summary = None
    if request.method == 'POST' and form.is_valid():
        try:
            summary = import_products_csv_for_supermarket(form.cleaned_data['file'], profile.supermarket)
        except CSVImportError as exc:
            form.add_error('file', str(exc))
        else:
            if summary['errors']:
                messages.warning(request, 'Importacao concluida com erros em algumas linhas.')
            else:
                messages.success(request, 'Importacao concluida com sucesso.')

    return render(request, 'market_panel/import_csv.html', {'profile': profile, 'form': form, 'summary': summary})


@login_required(login_url='market-login')
def order_list(request):
    profile, response = require_supermarket_profile(request)
    if response:
        return response

    orders = Order.objects.filter(supermarket=profile.supermarket).order_by('-created_at')
    status = (request.GET.get('status') or '').strip()
    date_from = (request.GET.get('date_from') or '').strip()
    date_to = (request.GET.get('date_to') or '').strip()
    query = (request.GET.get('q') or '').strip()

    if status:
        orders = orders.filter(status=status)
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    if query:
        orders = orders.filter(Q(code__icontains=query) | Q(customer_name__icontains=query))

    base_orders = Order.objects.filter(supermarket=profile.supermarket)
    summary = {
        status_value: base_orders.filter(status=status_value).count()
        for status_value, _ in Order.STATUS_CHOICES
    }
    context = {
        'profile': profile,
        'orders': orders,
        'summary': summary,
        'status_choices': Order.STATUS_CHOICES,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
        'query': query,
    }
    return render(request, 'market_panel/order_list.html', context)


@login_required(login_url='market-login')
def order_detail(request, pk):
    profile, response = require_supermarket_profile(request)
    if response:
        return response

    order = get_object_or_404(
        Order.objects.select_related('supermarket').prefetch_related('items', 'status_history__changed_by'),
        pk=pk,
        supermarket=profile.supermarket,
    )
    status_form = OrderStatusForm(instance=order)
    notes_form = OrderInternalNotesForm(instance=order)
    original_status = order.status

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_status':
            status_form = OrderStatusForm(request.POST, instance=order)
            if status_form.is_valid():
                updated_order = status_form.save(commit=False)
                new_status = updated_order.status
                if original_status != new_status:
                    updated_order.save(update_fields=['status', 'updated_at'])
                    OrderStatusHistory.objects.create(
                        order=order,
                        old_status=original_status,
                        new_status=new_status,
                        changed_by=request.user,
                        note=status_form.cleaned_data.get('status_note') or '',
                    )
                    messages.success(request, 'Status do pedido atualizado.')
                else:
                    messages.info(request, 'O status selecionado ja estava aplicado.')
                return redirect('market-order-detail', pk=order.pk)
        elif action == 'update_internal_notes':
            notes_form = OrderInternalNotesForm(request.POST, instance=order)
            if notes_form.is_valid():
                notes_form.save()
                messages.success(request, 'Observacao interna salva.')
                return redirect('market-order-detail', pk=order.pk)

    context = {
        'profile': profile,
        'order': order,
        'status_form': status_form,
        'notes_form': notes_form,
        'call_customer_whatsapp_url': build_customer_whatsapp_url(order, summary=False),
        'summary_whatsapp_url': build_customer_whatsapp_url(order, summary=True),
        'has_valid_customer_phone': bool(clean_phone(order.customer_phone)),
    }
    return render(request, 'market_panel/order_detail.html', context)


def clean_phone(phone):
    digits = ''.join(character for character in (phone or '') if character.isdigit())
    if len(digits) < 10:
        return ''
    return digits


def build_customer_whatsapp_url(order, summary=False):
    phone_digits = clean_phone(order.customer_phone)
    if not phone_digits:
        return None

    if summary:
        lines = [
            f'Pedido/orcamento {order.code}',
            f'Supermercado: {order.supermarket.name}',
            'Itens:',
        ]
        for item in order.items.all():
            lines.append(f'- {item.product_name_snapshot} x{item.quantity}: R$ {item.subtotal}')
        lines.append(f'Total estimado: R$ {order.total_amount}')
        lines.append(f'Status: {order.get_status_display()}')
    else:
        lines = [
            f'Ola, {order.customer_name}.',
            f'Recebemos seu pedido #{order.code} no {order.supermarket.name}.',
            'Estamos analisando e em breve retornamos.',
        ]

    return f'https://wa.me/55{phone_digits}?text={quote(chr(10).join(lines))}'
