from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from orders.models import Order

from .customer_forms import CustomerLoginForm, CustomerProfileForm, CustomerRegistrationForm
from .models import CustomerProfile


def customer_register(request):
    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        return redirect('customer-dashboard')

    form = CustomerRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Cadastro criado com sucesso.')
        return redirect('customer-dashboard')

    return render(request, 'customer/register.html', {'form': form})


def customer_login(request):
    if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
        return redirect('customer-dashboard')

    form = CustomerLoginForm(request, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('customer-dashboard')

    return render(request, 'customer/login.html', {'form': form})


def customer_logout(request):
    logout(request)
    return redirect('home')


def get_or_create_customer_profile(user):
    profile, _ = CustomerProfile.objects.get_or_create(
        user=user,
        defaults={'phone': ''},
    )
    return profile


@login_required(login_url='customer-login')
def customer_dashboard(request):
    profile = get_or_create_customer_profile(request.user)
    orders = Order.objects.filter(customer_user=request.user).select_related('supermarket').order_by('-created_at')
    return render(request, 'customer/dashboard.html', {
        'profile': profile,
        'orders_count': orders.count(),
        'recent_orders': orders[:5],
    })


@login_required(login_url='customer-login')
def customer_profile(request):
    profile = get_or_create_customer_profile(request.user)
    form = CustomerProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Perfil atualizado com sucesso.')
        return redirect('customer-profile')

    return render(request, 'customer/profile.html', {'form': form})


@login_required(login_url='customer-login')
def customer_orders(request):
    orders = Order.objects.filter(customer_user=request.user).select_related('supermarket').order_by('-created_at')
    return render(request, 'customer/orders.html', {'orders': orders})


@login_required(login_url='customer-login')
def customer_order_detail(request, code):
    order = get_object_or_404(
        Order.objects.select_related('supermarket').prefetch_related('items'),
        code=code.upper(),
        customer_user=request.user,
    )
    whatsapp_url = build_supermarket_whatsapp_url(order)
    return render(request, 'customer/order_detail.html', {'order': order, 'whatsapp_url': whatsapp_url})


def build_supermarket_whatsapp_url(order):
    phone_digits = ''.join(character for character in order.supermarket.phone if character.isdigit())
    if not phone_digits:
        return None

    message = f'Ola, gostaria de acompanhar o pedido {order.code}.'
    return f'https://wa.me/55{phone_digits}?text={quote(message)}'
