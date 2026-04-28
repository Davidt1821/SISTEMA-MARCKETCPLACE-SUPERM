import re
from decimal import Decimal

from django import forms

from .models import Order


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label='Nome', max_length=150)
    customer_phone = forms.CharField(label='Telefone', max_length=30)
    fulfillment_method = forms.ChoiceField(label='Tipo de atendimento', choices=Order.FULFILLMENT_CHOICES)
    delivery_street = forms.CharField(label='Rua', max_length=150, required=False)
    delivery_number = forms.CharField(label='Numero', max_length=30, required=False)
    delivery_district = forms.CharField(label='Bairro', max_length=100, required=False)
    delivery_city = forms.CharField(label='Cidade', max_length=100, required=False)
    delivery_complement = forms.CharField(label='Complemento', max_length=150, required=False)
    delivery_reference = forms.CharField(label='Referencia', max_length=150, required=False)
    notes = forms.CharField(label='Observacoes', required=False, widget=forms.Textarea(attrs={'rows': 3}))

    def __init__(self, *args, supermarket=None, products_total=Decimal('0.00'), **kwargs):
        super().__init__(*args, **kwargs)
        self.supermarket = supermarket
        self.products_total = products_total
        choices = [(Order.FULFILLMENT_ARRANGE, 'Combinar com o mercado')]
        if supermarket and supermarket.pickup_available:
            choices.insert(0, (Order.FULFILLMENT_PICKUP, 'Retirada no supermercado'))
        if supermarket and supermarket.delivery_available:
            insert_at = 1 if supermarket.pickup_available else 0
            choices.insert(insert_at, (Order.FULFILLMENT_DELIVERY, 'Entrega em casa'))
        self.fields['fulfillment_method'].choices = choices

    def clean_customer_phone(self):
        phone = self.cleaned_data['customer_phone'].strip()
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            raise forms.ValidationError('Informe um telefone valido com DDD.')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        fulfillment_method = cleaned_data.get('fulfillment_method')

        if fulfillment_method == Order.FULFILLMENT_DELIVERY:
            if self.supermarket and not self.supermarket.delivery_available:
                raise forms.ValidationError('Este supermercado nao oferece entrega.')
            required_fields = ['delivery_street', 'delivery_number', 'delivery_district', 'delivery_city']
            for field_name in required_fields:
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, 'Campo obrigatorio para entrega.')

        if fulfillment_method == Order.FULFILLMENT_PICKUP and self.supermarket and not self.supermarket.pickup_available:
            raise forms.ValidationError('Este supermercado nao oferece retirada.')

        return cleaned_data


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
