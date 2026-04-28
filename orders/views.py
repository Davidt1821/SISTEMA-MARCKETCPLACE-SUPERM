from urllib.parse import quote

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from public_pages.shopping_list import SESSION_KEY, get_session_list
from supermarkets.models import Supermarket

from .forms import CheckoutForm
from .models import Order
from .services import build_order_preview, create_order_from_preview


def checkout(request, supermarket_id):
    supermarket = get_object_or_404(Supermarket, pk=supermarket_id, is_active=True)
    session_items = get_session_list(request)
    if not session_items:
        messages.warning(request, 'Adicione produtos a lista antes de finalizar um pedido.')
        return redirect('shopping-list')

    preview = build_order_preview(session_items, supermarket)
    if not preview['available_items']:
        messages.warning(request, 'Este supermercado nao possui produtos disponiveis da sua lista.')
        return redirect('shopping-list')

    form = CheckoutForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        order = create_order_from_preview(supermarket, form.cleaned_data, preview)
        request.session[SESSION_KEY] = {}
        request.session.modified = True
        messages.success(request, f'Pedido {order.code} criado com sucesso.')
        return redirect('order-detail-public', code=order.code)

    return render(request, 'orders/checkout.html', {
        'form': form,
        'supermarket': supermarket,
        'preview': preview,
    })


def order_detail(request, code):
    order = get_object_or_404(
        Order.objects.select_related('supermarket').prefetch_related('items'),
        code=code.upper(),
    )
    whatsapp_url = build_whatsapp_url(order)
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'whatsapp_url': whatsapp_url,
    })


def order_receipt(request, code):
    order = get_object_or_404(
        Order.objects.select_related('supermarket').prefetch_related('items'),
        code=code.upper(),
    )
    return render(request, 'orders/order_receipt.html', {'order': order})


def build_whatsapp_url(order):
    phone_digits = ''.join(character for character in order.supermarket.phone if character.isdigit())
    if not phone_digits:
        return None

    lines = [
        f'Pedido/orcamento {order.code}',
        f'Cliente: {order.customer_name}',
        'Itens:',
    ]
    for item in order.items.all():
        lines.append(f'- {item.product_name_snapshot} x{item.quantity}: R$ {item.subtotal}')
    lines.append(f'Total estimado: R$ {order.total_amount}')

    return f'https://wa.me/55{phone_digits}?text={quote(chr(10).join(lines))}'
