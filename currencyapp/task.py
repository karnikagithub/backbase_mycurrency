import asyncio
import aiohttp
from celery import shared_task
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import CurrencyExchangeRate, ProviderClass



def get_providers():
    return ProviderClass.objects.filter(is_active=True).order_by("priority")

### Efficiently fetches data from exchange rate providers.
async def fetch_exchange_rate(session, provider, base_currency, target_currency, date):
    url = provider.get_historical_url(base_currency, target_currency, date)
    headers = {"Authorization": f"Bearer {provider.encrypted_api_key}"}
    
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return {
                "base_currency": base_currency,
                "target_currency": target_currency,
                "rate": data.get("rate"),
                "date": date,
                "provider": provider,
            }
        return None


async def fetch_and_store_rates(base_currency, target_currency, start_date, end_date):
    providers = get_providers()
    if not providers:
        return "No active providers available."
    
    tasks = []
    async with aiohttp.ClientSession() as session:
        for provider in providers:
            for days in range((end_date - start_date).days + 1):
                date = start_date + timedelta(days=days)
                tasks.append(fetch_exchange_rate(session, provider, base_currency, target_currency, date))
                
        results = await asyncio.gather(*tasks)
        
        for result in results:
            if result and result["rate"]:
                CurrencyExchangeRate.objects.update_or_create(
                    base_currency=result["base_currency"],
                    target_currency=result["target_currency"],
                    date=make_aware(datetime.strptime(result["date"], "%Y-%m-%d")),
                    defaults={
                        "rate": result["rate"],
                        "provider": result["provider"],
                    },
                )
    return "Historical data loaded successfully."



@shared_task
def load_historical_exchange_rates(base_currency, target_currency, start_date, end_date):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(fetch_and_store_rates(base_currency, target_currency, start_date, end_date))
