"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter

from prices.views import ProductPriceViewSet
from products.views import CategoryViewSet, ProductViewSet
from promotions.views import PromotionViewSet
from search.views import CompareProductPricesView, SearchProductsView
from supermarkets.views import SupermarketViewSet

admin.site.site_header = 'Painel Administrativo do Marketplace'
admin.site.site_title = 'Admin do Marketplace'
admin.site.index_title = 'Gerenciamento do sistema'

router = DefaultRouter()
router.register('supermarkets', SupermarketViewSet, basename='supermarket')
router.register('categories', CategoryViewSet, basename='category')
router.register('products', ProductViewSet, basename='product')
router.register('prices', ProductPriceViewSet, basename='price')
router.register('promotions', PromotionViewSet, basename='promotion')

urlpatterns = [
    path('', include('public_pages.urls')),
    path('mercado/', include('accounts.urls')),
    path(
        'admin/importar-csv/',
        admin.site.admin_view(
            RedirectView.as_view(
                pattern_name='admin:products_product_import_csv',
                permanent=False,
            )
        ),
        name='admin-importar-csv',
    ),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/search/', SearchProductsView.as_view(), name='search-products'),
    path('api/compare/', CompareProductPricesView.as_view(), name='compare-product-prices'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
