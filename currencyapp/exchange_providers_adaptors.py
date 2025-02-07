from abc import ABC, abstractmethod
import random
import requests
from datetime import date
import logging
from .models import ProviderClass

logger = logging.getLogger("exchange_rate")

class ExchangeRateProvider(ABC):
    """Abstract Base Class for Exchange Rate Providers."""

    def __init__(self, provider: ProviderClass):
        self.provider = provider

    @abstractmethod
    def get_rate(self, source_currency, exchanged_currency, valuation_date):
        """Fetch live exchange rate data."""
        pass

    @abstractmethod
    def get_historical_rate(self, source_currency, exchanged_currency, valuation_date):
        """Fetch historical exchange rate data."""
        pass


class CurrencyBeaconProvider(ExchangeRateProvider):

    """CurrencyBeacon integration."""

    BASE_URL = "https://api.currencybeacon.com/v1/exchange"

    def get_rate(self, source_currency, exchanged_currency, valuation_date):
        """Fetch current exchange rate."""
        return self._fetch_rate(source_currency, exchanged_currency, valuation_date)

    def get_historical_rate(self, source_currency, exchanged_currency, valuation_date):
        """Fetch historical exchange rate."""
        try:
            api_key = self.provider.get_api_key()
            api_url = self.provider.api_url.rstrip('/')
            endpoint = f"{api_url}/historical"
            params = {
                "base": source_currency.code,
                "symbols": exchanged_currency.code,
                "date": valuation_date.strftime("%Y-%m-%d"),
                "api_key": api_key,
            }
            response = requests.get(endpoint, params=params)
            data = response.json()

            if response.status_code == 200 and "rates" in data:
                return data["rates"].get(exchanged_currency.code)
        except Exception as e:
            logger.error(f"CurrencyBeaconProvider error: {e}", exc_info=True)
        return None

    def _fetch_rate(self, source_currency, exchanged_currency, valuation_date):
        """Internal method to fetch exchange rates from CurrencyBeacon API."""
        try:
            api_key = self.provider.get_api_key()
            api_url = self.provider.api_url
            params = {
                "from": source_currency.code,
                "to": exchanged_currency.code,
                "date": valuation_date.strftime("%Y-%m-%d"),
                "api_key": api_key,
            }
            # response = requests.get(api_url, params=params)
            response = requests.get(self.BASE_URL, params=params)
            data = response.json()

            if response.status_code == 200 and "rate" in data:
                logger.info(
                    f"CurrencyBeacon: {source_currency.code} → {exchanged_currency.code} "
                    f"on {valuation_date}: {data['rate']}"
                )
                return data["rate"]
            else:
                logger.warning(
                    f"CurrencyBeacon failed: {response.status_code}, Response: {data}"
                )
        except Exception as e:
            logger.error(f"CurrencyBeacon error: {e}", exc_info=True)
        return None
    
    def convert_currency(self, source_currency, exchanged_currency, amount):
        """Convert an amount from one currency to another."""
        try:
            api_key = self.provider.get_api_key()
            api_url = self.provider.api_url.rstrip('/')
            endpoint = f"{api_url}/convert"
            params = {
                "from": source_currency.code,
                "to": exchanged_currency.code,
                "amount": amount,
                "api_key": api_key,
            }
            response = requests.get(endpoint, params=params)
            data = response.json()

            if response.status_code == 200 and "result" in data:
                return data["result"]
        except Exception as e:
            logger.error(f"CurrencyBeaconProvider conversion error: {e}", exc_info=True)
        return None


class MockExchangeRateProvider(ExchangeRateProvider):
    """Mock provider generating random exchange rates."""

    def get_rate(self, source_currency, exchanged_currency, valuation_date):
        """Generate a random exchange rate (live)."""
        return self._generate_mock_rate(source_currency, exchanged_currency, valuation_date)

    def get_historical_rate(self, source_currency, exchanged_currency, valuation_date):
        """Generate a random exchange rate (historical)."""
        return self._generate_mock_rate(source_currency, exchanged_currency, valuation_date)

    def _generate_mock_rate(self, source_currency, exchanged_currency, valuation_date):
        """Internal mock rate generator."""
        rate = round(random.uniform(0.5, 1.5), 6)
        logger.info(
            f"MockProvider: Generated {source_currency.code} → {exchanged_currency.code} rate "
            f"on {valuation_date}: {rate}"
        )
        return rate
