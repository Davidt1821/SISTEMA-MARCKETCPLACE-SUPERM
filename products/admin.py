from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import path

from .models import Category, Product
from .services.csv_importer import CSVImportError, import_products_csv


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'barcode', 'is_active', 'created_at']
    list_filter = ['category', 'brand', 'is_active']
    search_fields = ['name', 'brand', 'barcode']
    change_list_template = 'admin/products/product_changelist.html'
    change_form_template = 'admin/products/product_change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'import-csv/',
                self.admin_site.admin_view(self.import_csv_view),
                name='products_product_import_csv',
            ),
        ]
        return custom_urls + urls

    def import_csv_view(self, request):
        if not request.user.is_active or not request.user.is_staff:
            raise PermissionDenied

        form = CSVImportForm(request.POST or None, request.FILES or None)
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Importar produtos por CSV',
            'form': form,
            'summary': None,
        }

        if request.method == 'POST' and form.is_valid():
            try:
                summary = import_products_csv(form.cleaned_data['file'])
            except CSVImportError as exc:
                form.add_error('file', str(exc))
            else:
                context['summary'] = summary
                if summary['errors']:
                    messages.warning(request, 'Importacao concluida com erros em algumas linhas.')
                else:
                    messages.success(request, 'Importacao concluida com sucesso.')
                return render(request, 'admin/products/import_csv.html', context)

        return render(request, 'admin/products/import_csv.html', context)


class CSVImportForm(forms.Form):
    file = forms.FileField(label='Arquivo CSV')

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.lower().endswith('.csv'):
            raise forms.ValidationError('Envie um arquivo com extensao .csv.')
        return file
