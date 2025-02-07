import logging
from datetime import date, timedelta
from .models import ProviderClass, Currency, CurrencyExchangeRate
from .exchange_rate_factory import ExchangeRateProviderFactory

logger = logging.getLogger("exchange_rate")

def get_exchange_rate_data(source_currency: Currency, exchanged_currency: Currency, valuation_date: date, provider: ProviderClass = None):
    """Retrieve exchange rate data using Adapter Pattern with logging."""
    
    logger.info(
        "Fetching exchange rate for %s -> %s on %s using %s",
        source_currency.code,
        exchanged_currency.code,
        valuation_date,
        provider.name if provider else "auto-selection",
    )

    # If a specific provider is requested, try it first
    if provider:
        provider_instance = ExchangeRateProviderFactory.get_provider_instance(provider)
        if provider_instance:
            rate = provider_instance.get_rate(source_currency, exchanged_currency, valuation_date)
            if rate:
                logger.info(f"Using {provider.name}: {rate}")
                return rate
            else:
                logger.warning(f"{provider.name} failed, attempting fallback.")

    # Iterate through active providers in priority order
    for provider in ExchangeRateProviderFactory.get_active_providers():
        provider_instance = ExchangeRateProviderFactory.get_provider_instance(provider)
        if provider_instance:
            rate = provider_instance.get_rate(source_currency, exchanged_currency, valuation_date)
            if rate:
                logger.info(f"Using {provider.name}: {rate}")
                return rate
            else:
                logger.warning(f"{provider.name} failed, trying next provider.")

    logger.error(
        f"Failed to retrieve exchange rate for {source_currency.code} → {exchanged_currency.code} on {valuation_date}"
    )
    return None


def fetch_historical_data(source_currency: Currency, exchanged_currency: Currency, start_date: date, end_date: date):
    """Fetch historical exchange rate data for a given date range."""
    
    logger.info(f"Fetching historical data from {start_date} to {end_date} for {source_currency.code} -> {exchanged_currency.code}")
    
    active_providers = ExchangeRateProviderFactory.get_active_providers()
    
    if not active_providers:
        logger.error("No active providers available for historical data.")
        return False
    
    current_date = start_date
    while current_date <= end_date:
        for provider in active_providers:
            provider_instance = ExchangeRateProviderFactory.get_provider_instance(provider)
            if provider_instance:
                rate = provider_instance.get_historical_rate(source_currency, exchanged_currency, current_date)
                if rate:
                    CurrencyExchangeRate.objects.update_or_create(
                        source_currency=source_currency,
                        exchanged_currency=exchanged_currency,
                        valuation_date=current_date,
                        defaults={"exchange_rate": rate, "provider": provider}
                    )
                    logger.info(f"Stored exchange rate for {current_date}: {rate}")
                    break  # Exit loop if successful
                else:
                    logger.warning(f"Provider {provider.name} failed for {current_date}, trying next.")
        
        current_date += timedelta(days=1)
    
    logger.info("Historical data loading complete.")
    return True
