from django.contrib import admin
from .models import ProviderClass, Currency, CurrencyExchangeRate
from django.urls import path
from django.shortcuts import render
from .models import Currency
from .services import get_exchange_rate_data
from datetime import date
from django.http import JsonResponse

# Register your models here.


class CurrencyConverterAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('converter/', self.admin_site.admin_view(self.converter_view), name="currency_converter"),
        ]
        return custom_urls + urls

    def converter_view(self, request):
        if request.method == "POST":
            source_currency_code = request.POST.get("source_currency")
            target_currency_codes = request.POST.getlist("target_currencies")

            source_currency = Currency.objects.get(code=source_currency_code)
            exchange_rates = {}

            for target_code in target_currency_codes:
                target_currency = Currency.objects.get(code=target_code)
                rate = get_exchange_rate_data(source_currency, target_currency, date.today(), None)
                exchange_rates[target_code] = rate

            return JsonResponse({"exchange_rates": exchange_rates})

        return JsonResponse({"error": "Invalid request"}, status=400)

# admin.site.register(Currency)
admin.site.register(CurrencyExchangeRate)
admin.site.register(ProviderClass)
admin.site.register(Currency, CurrencyConverterAdmin)
