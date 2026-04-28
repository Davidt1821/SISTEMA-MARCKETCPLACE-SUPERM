from django.db.models import Count
from django.views.generic import TemplateView

from products.models import Category
from search.querysets import active_promotions_queryset, comparison_products_queryset, search_products_queryset


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
        context['promotions'] = active_promotions_queryset()
        return context
