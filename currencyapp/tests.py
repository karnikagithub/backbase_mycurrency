import random
from datetime import date
from unittest.mock import patch, MagicMock
from django.test import TestCase
from .models import ProviderClass, Currency
from .services import get_exchange_rate_data
from .exchange_rate_factory import ExchangeRateProviderFactory

class ExchangeRateServiceTests(TestCase):
    
    def setUp(self):
        """Set up test data for providers and currencies."""
        self.usd = Currency.objects.create(code="USD", name="US Dollar", symbol="$")
        self.eur = Currency.objects.create(code="EUR", name="Euro", symbol="€")

        # Create two providers with different priorities
        self.provider1 = ProviderClass.objects.create(name="CurrencyBeacon", is_active=True,
                                                       priority=1,encrypted_api_key="tlUAcRLtnU5wpnJ9cecbbSCaLVVPgEdy")
        self.provider2 = ProviderClass.objects.create(name="Mock", is_active=True, priority=2)

    @patch("currencyapp.exchange_providers_adaptors.CurrencyBeaconProvider.get_rate")
    @patch("currencyapp.exchange_providers_adaptors.MockExchangeRateProvider.get_rate")
    def test_get_exchange_rate_success(self, mock_mock_provider, mock_currency_beacon):
        """Test retrieving exchange rate successfully from the highest priority provider."""
        mock_currency_beacon.return_value = 1.234567  # Simulate API success
        rate = get_exchange_rate_data(self.usd, self.eur, date.today())

        self.assertEqual(rate, 1.234567)
        mock_currency_beacon.assert_called_once()  # Ensures only the first provider was used
        mock_mock_provider.assert_not_called()  # No fallback required

    @patch("currencyapp.exchange_providers_adaptors.CurrencyBeaconProvider.get_rate")
    @patch("currencyapp.exchange_providers_adaptors.MockExchangeRateProvider.get_rate")
    def test_fallback_to_mock_provider(self, mock_mock_provider, mock_currency_beacon):
        """Test fallback to the next provider when the first one fails."""
        mock_currency_beacon.return_value = None  # Simulate failure
        mock_mock_provider.return_value = 0.987654  # Mock returns valid rate

        rate = get_exchange_rate_data(self.usd, self.eur, date.today())

        self.assertEqual(rate, 0.987654)
        mock_currency_beacon.assert_called_once()  # First provider failed
        mock_mock_provider.assert_called_once()  # Second provider used

    @patch("currencyapp.exchange_providers_adaptors.CurrencyBeaconProvider.get_rate")
    @patch("currencyapp.exchange_providers_adaptors.MockExchangeRateProvider.get_rate")
    def test_all_providers_fail(self, mock_mock_provider, mock_currency_beacon):
        """Test when all providers fail, should return None."""
        mock_currency_beacon.return_value = None
        mock_mock_provider.return_value = None

        rate = get_exchange_rate_data(self.usd, self.eur, date.today())

        self.assertIsNone(rate)  # No valid rates found
        mock_currency_beacon.assert_called_once()
        mock_mock_provider.assert_called_once()

    def test_get_active_providers(self):
        """Ensure only active providers are retrieved and sorted by priority."""
        self.provider2.is_active = False
        self.provider2.save()

        active_providers = ExchangeRateProviderFactory.get_active_providers()

        self.assertEqual(len(active_providers), 1)
        self.assertEqual(active_providers[0].name, "CurrencyBeacon")
