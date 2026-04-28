from urllib.parse import quote

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from public_pages.shopping_list import SESSION_KEY, get_session_list
from supermarkets.models import Supermarket

from .forms import CheckoutForm
from .models import Order
from .services import build_order_preview, calculate_delivery_fee, create_order_from_preview


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

    initial = get_checkout_initial(request)
    form = CheckoutForm(request.POST or None, supermarket=supermarket, products_total=preview['total'], initial=initial)
    selected_fulfillment = (
        request.POST.get('fulfillment_method')
        or form.fields['fulfillment_method'].choices[0][0]
    )
    estimated_delivery_fee = calculate_delivery_fee(supermarket, preview['total'], selected_fulfillment)
    estimated_final_total = preview['total'] + estimated_delivery_fee

    if request.method == 'POST' and form.is_valid():
        order = create_order_from_preview(
            supermarket,
            form.cleaned_data,
            preview,
            customer_user=request.user if request.user.is_authenticated else None,
        )
        request.session[SESSION_KEY] = {}
        request.session.modified = True
        messages.success(request, f'Pedido {order.code} criado com sucesso.')
        return redirect('order-detail-public', code=order.code)

    return render(request, 'orders/checkout.html', {
        'form': form,
        'supermarket': supermarket,
        'preview': preview,
        'estimated_delivery_fee': estimated_delivery_fee,
        'estimated_final_total': estimated_final_total,
    })


def get_checkout_initial(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'customer_profile'):
        return {}

    profile = request.user.customer_profile
    return {
        'customer_name': request.user.get_full_name() or request.user.username,
        'customer_phone': profile.phone,
        'delivery_street': profile.default_street,
        'delivery_number': profile.default_number,
        'delivery_district': profile.default_district,
        'delivery_city': profile.default_city,
        'delivery_complement': profile.default_complement,
        'delivery_reference': profile.default_reference,
    }


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
    lines.append(f'Tipo de atendimento: {order.get_fulfillment_method_display()}')
    if order.fulfillment_method == Order.FULFILLMENT_DELIVERY and order.delivery_address:
        lines.append(f'Endereco: {order.delivery_address}')
    lines.append(f'Taxa de entrega: R$ {order.delivery_fee}')
    lines.append(f'Total estimado: R$ {order.final_total}')

    return f'https://wa.me/55{phone_digits}?text={quote(chr(10).join(lines))}'
