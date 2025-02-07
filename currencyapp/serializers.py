from rest_framework import serializers
from .models import Currency, CurrencyExchangeRate, ProviderClass



class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

class CurrencyExchangeRateSerializer(serializers.ModelSerializer):
    source_currency = CurrencySerializer(read_only=True)
    exchanged_currency = CurrencySerializer(read_only=True)
    
    class Meta:
        model = CurrencyExchangeRate
        fields = '__all__'

class ProviderClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderClass
        fields = '__all__'


class ExchangeRateSerializer(serializers.ModelSerializer):
    source_currency = CurrencySerializer(read_only=True)
    exchanged_currency = CurrencySerializer(read_only=True)
    provider = ProviderClassSerializer(read_only=True)

    class Meta:
        model = CurrencyExchangeRate
        fields = "__all__"


class ConversionSerializer(serializers.Serializer):
    source_currency = serializers.CharField()
    exchanged_currency = serializers.CharField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=6)
    exchange_rate = serializers.DecimalField(max_digits=20, decimal_places=6, read_only=True)
    converted_amount = serializers.DecimalField(max_digits=20, decimal_places=6, read_only=True)
