from django.urls import path
from .views import CurrencyViewSet, ExchangeRateView, currency_conversion
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet)

urlpatterns = [
    path('exchange-rates/', ExchangeRateView.as_view(), name='exchange-rates'),
    path('convert/', currency_conversion, name='currency-conversion'),
]

urlpatterns += router.urls
