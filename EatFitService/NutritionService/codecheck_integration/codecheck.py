
from NutritionService.serializers import ProductSerializer


USER = 'autoidlabs2'
SECRET = '752DAB062D3E82189918234DF10D175E77DA07DF051FA324BBC8ADD543919DEC'  # Note it is in hex


def search_for_gtins(gtins):
    created_products, not_found_gtins = __import_products(gtins)
    return {'products': ProductSerializer(created_products, many=True).data,
            'not_found_gtins': not_found_gtins}


def __import_products(gtins):
    return [], []
