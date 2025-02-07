from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
import base64

# Create your models here.


# Generate a key (Do this once and store it in settings)
if not hasattr(settings, 'ENCRYPTION_KEY'):
    settings.ENCRYPTION_KEY = base64.urlsafe_b64encode(Fernet.generate_key()).decode()


class ProtectedModel(models.Model):
    class Meta:
        abstract = True
    
    def delete(self, *args, **kwargs):
        raise NotImplementedError("Delete is not allowed/restricted for this model")
    

class Currency(ProtectedModel):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, db_index=True)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return f"Currency: {self.name} & it's related {self.code}"
    

class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(Currency, related_name="exchanges",on_delete=models.CASCADE)
    exchanged_currency = models.ForeignKey(Currency,on_delete=models.CASCADE)
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(db_index=True, decimal_places=6,max_digits=10)

    def __str__(self):
        return f"{self.source_currency} to {self.exchanged_currency} on {self.valuation_date}: of Rate{self.rate_value}"
    

class ProviderClass(models.Model):
    name = models.CharField(max_length=100,unique=True)
    api_url = models.URLField(help_text="API URL of the provider")
    encrypted_api_key = models.TextField()
    priority = models.PositiveIntegerField(default=1,help_text="lower the number means higher priority")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (Priority:{self.priority}, Active:{self.is_active})"
    

    def set_api_key(self, raw_key):
            """Encrypt and store the API key."""
            cipher = Fernet(settings.ENCRYPTION_KEY)
            self.encrypted_api_key = cipher.encrypt(raw_key.encode()).decode()

    def get_api_key(self):
        """Decrypt and return the API key."""
        if self.encrypted_api_key:
            cipher = Fernet(settings.ENCRYPTION_KEY)
            return cipher.decrypt(self.encrypted_api_key.encode()).decode()
    
        return None
    
    apikey = property(get_api_key, set_api_key)

    def __str__(self):
        return self.name

        


        
        