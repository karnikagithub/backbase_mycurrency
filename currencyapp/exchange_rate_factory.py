from .models import ProviderClass
from .exchange_providers_adaptors import CurrencyBeaconProvider, MockExchangeRateProvider



class ExchangeRateProviderFactory:
    
    """Factory class for creating exchange rate provider instances."""

    @staticmethod
    def get_active_providers():
        """Retrieve active providers sorted by priority."""
        return ProviderClass.objects.filter(is_active=True).order_by("priority")

    @staticmethod
    def get_provider_instance(provider: ProviderClass):
        """Return an instance of the correct provider class."""
        provider_mapping = {
            "CurrencyBeacon": CurrencyBeaconProvider,
            "Mock": MockExchangeRateProvider,
        }

        provider_class = provider_mapping.get(provider.name)
        if provider_class:
            return provider_class(provider)
        return None
