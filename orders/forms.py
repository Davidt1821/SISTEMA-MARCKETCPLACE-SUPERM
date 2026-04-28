import re

from django import forms

from .models import Order


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(label='Nome', max_length=150)
    customer_phone = forms.CharField(label='Telefone', max_length=30)
    customer_address = forms.CharField(label='Endereco', max_length=255, required=False)
    notes = forms.CharField(label='Observacoes', required=False, widget=forms.Textarea(attrs={'rows': 3}))

    def clean_customer_phone(self):
        phone = self.cleaned_data['customer_phone'].strip()
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            raise forms.ValidationError('Informe um telefone valido com DDD.')
        return phone


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
