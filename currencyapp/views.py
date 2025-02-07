from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils.dateparse import parse_date
from datetime import date
from .models import Currency, CurrencyExchangeRate, ProviderClass
from .serializers import CurrencySerializer, CurrencyExchangeRateSerializer, ProviderClassSerializer, ExchangeRateSerializer, ConversionSerializer
from .services import get_exchange_rate_data
from rest_framework.views import APIView
from .exchange_rate_factory import ExchangeRateProviderFactory

# Create your views here.


# Currency CRUD API
class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class CurrencyExchangeRateViewSet(viewsets.ModelViewSet):
    queryset = CurrencyExchangeRate.objects.all()
    serializer_class = CurrencyExchangeRateSerializer

class ProviderClassViewSet(viewsets.ModelViewSet):
    queryset = ProviderClass.objects.all()
    serializer_class = ProviderClassSerializer



# class ExchangeRateView(APIView):
#     """
#     Handles retrieving and adding exchange rates.
#     Supports:
#     - GET: Retrieve exchange rates for a time period.
#     - POST: Add new exchange rates.
#     """

#     def get(self, request):
#         """Retrieve exchange rates for a given date range."""
#         source_currency = request.query_params.get("source_currency")
#         date_from = parse_date(request.query_params.get("date_from"))
#         date_to = parse_date(request.query_params.get("date_to"))

#         if not source_currency or not date_from or not date_to:
#             return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

#         if date_from > date_to:
#             return Response({"error": "Invalid date range"}, status=status.HTTP_400_BAD_REQUEST)

#         queryset = CurrencyExchangeRate.objects.filter(
#             source_currency__code=source_currency,
#             valuation_date__range=(date_from, date_to)
#         )

#         if not queryset.exists():
#             return Response({"message": "No exchange rates found"}, status=status.HTTP_404_NOT_FOUND)

#         serializer = ExchangeRateSerializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request):
#         """Add a new exchange rate or update if it already exists."""
#         serializer = ExchangeRateSerializer(data=request.data)

#         if serializer.is_valid():
#             source_currency = serializer.validated_data["source_currency"]
#             exchanged_currency = serializer.validated_data["exchanged_currency"]
#             valuation_date = serializer.validated_data["valuation_date"]
#             rate_value = serializer.validated_data["rate_value"]

#             # Check if rate already exists for the given date
#             existing_rate = CurrencyExchangeRate.objects.filter(
#                 source_currency__code=source_currency,
#                 exchanged_currency__code=exchanged_currency,
#                 valuation_date=valuation_date
#             ).first()

#             if existing_rate:
#                 # Update existing rate
#                 existing_rate.rate_value = rate_value
#                 existing_rate.save()
#                 return Response({"message": "Exchange rate updated successfully"}, status=status.HTTP_200_OK)
#             else:
#                 # Create new rate
#                 serializer.save()
#                 return Response({"message": "Exchange rate added successfully"}, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Convert amount between currencies
@api_view(['GET'])
def currency_conversion(request):
    source_currency_code = request.query_params.get("source_currency")
    exchanged_currency_code = request.query_params.get("exchanged_currency")
    amount = request.query_params.get("amount")
    
    if not source_currency_code or not exchanged_currency_code or not amount:
        return Response({"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        amount = float(amount)
        source_currency = Currency.objects.get(code=source_currency_code)
        exchanged_currency = Currency.objects.get(code=exchanged_currency_code)
    except (ValueError, Currency.DoesNotExist):
        return Response({"error": "Invalid currency or amount"}, status=status.HTTP_400_BAD_REQUEST)
    
    rate = get_exchange_rate_data(source_currency, exchanged_currency, date.today())
    if rate is None:
        return Response({"error": "Exchange rate not available"}, status=status.HTTP_404_NOT_FOUND)
    
    converted_amount = rate * amount
    return Response({"rate": rate, "converted_amount": converted_amount})




class ExchangeRateView(generics.ListAPIView):
    serializer_class = ExchangeRateSerializer

    def get_queryset(self):
        source_currency = self.request.query_params.get("source_currency")
        date_from = parse_date(self.request.query_params.get("date_from"))
        date_to = parse_date(self.request.query_params.get("date_to"))
        
        if not source_currency or not date_from or not date_to:
            return CurrencyExchangeRate.objects.none()
        
        queryset = CurrencyExchangeRate.objects.filter(
            source_currency__code=source_currency,
            valuation_date__range=(date_from, date_to)
        )

        # If no data found, fetch from providers
        if not queryset.exists():
            source_currency_obj = Currency.objects.get(code=source_currency)
            active_providers = ExchangeRateProviderFactory.get_active_providers()
            
            for valuation_date in [date_from, date_to]:
                for provider in active_providers:
                    provider_instance = ExchangeRateProviderFactory.get_provider_instance(provider)
                    if provider_instance:
                        rate = provider_instance.get_rate(source_currency_obj, None, valuation_date)
                        if rate:
                            CurrencyExchangeRate.objects.create(
                                source_currency=source_currency_obj,
                                valuation_date=valuation_date,
                                rate=rate,
                                provider=provider
                            )
                            break  # Stop once data is fetched

            # Re-fetch the queryset with the newly stored data
            queryset = CurrencyExchangeRate.objects.filter(
                source_currency__code=source_currency,
                valuation_date__range=(date_from, date_to)
            )
        
        return queryset