import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from  currencyapp.models import ProviderClass, Currency, CurrencyExchangeRate

class Command(BaseCommand):
    help = "Seed initial providers, currencies, and exchange rates"

    def handle(self, *args, **kwargs):
        
        # Create Currencies
        currencies = [
            {"code": "USD", "name": "United States Dollar", "symbol": "$"},
            {"code": "EUR", "name": "Euro", "symbol": "€"},
            {"code": "GBP", "name": "British Pound", "symbol": "£"},
        ]
        for currency_data in currencies:
            Currency.objects.get_or_create(code=currency_data["code"], defaults=currency_data)

        usd = Currency.objects.get(code="USD")
        eur = Currency.objects.get(code="EUR")
        gbp = Currency.objects.get(code="GBP")
        provider = ProviderClass.objects.get(name="CurrencyBeacon")

        # Create Exchange Rates for the past 10 days
        for i in range(10):
            valuation_date = datetime.today() - timedelta(days=i)
            rate_usd_eur = round(random.uniform(0.8, 1.2), 6)
            rate_usd_gbp = round(random.uniform(0.6, 0.9), 6)

            CurrencyExchangeRate.objects.update_or_create(
                source_currency=usd,
                exchanged_currency=eur,
                valuation_date=valuation_date,
                defaults={"rate": rate_usd_eur, "provider": provider},
            )
            CurrencyExchangeRate.objects.update_or_create(
                source_currency=usd,
                exchanged_currency=gbp,
                valuation_date=valuation_date,
                defaults={"rate": rate_usd_gbp, "provider": provider},
            )

        self.stdout.write(self.style.SUCCESS("Successfully loaded initial data."))
