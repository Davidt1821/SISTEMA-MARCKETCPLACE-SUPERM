from django.db.models import Count
from django.views.generic import TemplateView

from products.models import Category
from supermarkets.models import Supermarket
from search.querysets import active_promotions_queryset, comparison_products_queryset, search_products_queryset


def filter_options_context():
    return {
        'filter_categories': Category.objects.filter(is_active=True).order_by('name'),
        'filter_cities': (
            Supermarket.objects.filter(is_active=True)
            .exclude(city='')
            .values_list('city', flat=True)
            .distinct()
            .order_by('city')
        ),
        'filter_supermarkets': Supermarket.objects.filter(is_active=True).order_by('name'),
    }


class HomePageView(TemplateView):
    template_name = 'public_pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marketplace_name'] = 'Mercado da Cidade'
        context['categories'] = (
            Category.objects.filter(is_active=True)
            .annotate(product_count=Count('products'))
            .filter(product_count__gt=0)
            .order_by('-product_count', 'name')[:8]
        )
        context['featured_promotions'] = active_promotions_queryset()[:6]
        return context


class SearchPageView(TemplateView):
    template_name = 'public_pages/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = (self.request.GET.get('q') or '').strip()
        context['query'] = query
        context['selected_category'] = (self.request.GET.get('category') or '').strip()
        context['selected_city'] = (self.request.GET.get('city') or '').strip()
        context['selected_supermarket'] = (self.request.GET.get('supermarket') or '').strip()
        context.update(filter_options_context())
        context['products'] = search_products_queryset(self.request.GET, default_available=None) if query or self.request.GET else []
        return context


class ComparePageView(TemplateView):
    template_name = 'public_pages/compare.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = (self.request.GET.get('q') or '').strip()
        context['query'] = query
        context['products'] = comparison_products_queryset(query, default_available=None) if query else []
        return context


class PromotionsPageView(TemplateView):
    template_name = 'public_pages/promotions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = (self.request.GET.get('category') or '').strip()
        city = (self.request.GET.get('city') or '').strip()
        promotions = active_promotions_queryset()

        if category:
            promotions = promotions.filter(product__category__name__icontains=category)
        if city:
            promotions = promotions.filter(supermarket__city__icontains=city)

        context['selected_category'] = category
        context['selected_city'] = city
        context.update(filter_options_context())
        context['promotions'] = promotions
        return context
