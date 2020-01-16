import time
import requests
from EatFitService import settings
from SaltTrackerService.models import ReebateCredentials, MigrosBasket, MigrosItem, MigrosBasketItem
from SaltTrackerService.serializers import ReebateSerializer
import json
from TrustBoxAPI.models import ImportLog
from datetime import datetime

def get_customer_trace(username, password, millis):
    data = {'username':username, "password": password, "lastReceiptMillis" : millis} 
    r = requests.post(settings.REEBATE_URL, json=data)
    json_data = json.loads(r.content.decode("utf8"))
    serializer = ReebateSerializer(data=json_data)
    return serializer


def fill_db():
    reebate_users = ReebateCredentials.objects.using("salttracker").all()
    migros_items_list = MigrosItem.objects.using("salttracker").all()
    migros_items = {}
    for item in migros_items_list:
        migros_items[item.name] = item
    for reebate_user in reebate_users:
        if reebate_user.last_reebate_import:
            millis = reebate_user.last_reebate_import
        else:
            millis = int(round(time.time() * 1000)) - 63113852000
        serializer = get_customer_trace(reebate_user.username, reebate_user.password, millis)
        start_import = datetime.now()
        if serializer.is_valid():
            try:
                for basket in serializer.validated_data["receipts"]:
                    if basket:
                        m_basket = MigrosBasket.objects.using("salttracker").create(user=reebate_user.user, external_id=basket["externalId"], date_of_purchase_millis = basket["dateOfPurchaseInMillis"], store = basket["store"], added_date = datetime.now())
                        for item in basket["lineItems"]:
                            if item["name"] in migros_items:
                                m_item = migros_items[item["name"]]
                            else:
                                m_item = MigrosItem.objects.using("salttracker").create(name=item["name"])
                                migros_items[item["name"]] = m_item
                            MigrosBasketItem.objects.using("salttracker").create(migros_basket= m_basket, quantity = item["quantity"], price=item["price"], migros_item=m_item)
                reebate_user.last_reebate_import = int(round(time.time() * 1000))
                reebate_user.save()
            except Exception as e:
                 MigrosBasket.objects.using("salttracker").filter(user=reebate_user.user, added_date__gt=start_import).delete()
                 ImportLog.objects.create(import_timestamp = datetime.now(), successful=False, product_gtin = "", failed_reason = "Reebate Import: " + str(reebate_user.user.email) + " " + str(e))
