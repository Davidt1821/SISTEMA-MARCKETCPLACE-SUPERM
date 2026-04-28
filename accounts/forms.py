from django import forms

from prices.models import ProductPrice
from products.models import Product
from promotions.models import Promotion


class PriceForm(forms.ModelForm):
    class Meta:
        model = ProductPrice
        fields = ['price', 'old_price', 'available']
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'old_price': forms.NumberInput(attrs={'step': '0.01'}),
        }


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['product', 'promotional_price', 'start_date', 'end_date', 'description', 'is_active']
        widgets = {
            'promotional_price': forms.NumberInput(attrs={'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, supermarket=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.supermarket = supermarket
        self.fields['product'].queryset = (
            Product.objects.filter(prices__supermarket=supermarket, is_active=True)
            .select_related('category')
            .distinct()
            .order_by('name', 'brand')
        )

    def clean_product(self):
        product = self.cleaned_data['product']
        if not ProductPrice.objects.filter(product=product, supermarket=self.supermarket).exists():
            raise forms.ValidationError('Este produto nao possui preco cadastrado para o seu supermercado.')
        return product


class SupermarketCSVImportForm(forms.Form):
    file = forms.FileField(label='Arquivo CSV')

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.lower().endswith('.csv'):
            raise forms.ValidationError('Envie um arquivo com extensao .csv.')
        return file
