from django.urls import path

from .views import ComparePageView, HomePageView, PromotionsPageView, SearchPageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('buscar/', SearchPageView.as_view(), name='public-search'),
    path('comparar/', ComparePageView.as_view(), name='public-compare'),
    path('promocoes/', PromotionsPageView.as_view(), name='public-promotions'),
]
