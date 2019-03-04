from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class AzureMediaStorage(AzureStorage):
    account_name = 'eatfitmedias'
    account_key = settings.AZURE_STORAGE_KEY
    azure_container = 'media'
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = 'eatfitmedias'
    account_key = settings.AZURE_STORAGE_KEY
    azure_container = 'static'
    expiration_secs = None
