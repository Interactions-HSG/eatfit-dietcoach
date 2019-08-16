import json

def generate_request_long(r2n_partner, r2n_user):

    request = {
        "r2n_partner": r2n_partner,
        "r2n_username": r2n_user,
        "receipts": [
            {
                "receipt_id": "1549971885",
                "receipt_datetime": "2019-02-12T12:44:45Z",
                "business_unit": "Migros",
                "items": [
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    },
                    {
                        "article_id": "MClass MSC rosa Thon",
                        "article_type": "Migros_long_v1",
                        "quantity": 1,
                        "quantity_unit": "units",
                        "price": "1.9",
                        "price_currency": "CHF"
                    }
                ]
            }
        ]
    }

    return request


def example_openfood_request():
    response = {u'data': [{u'alcohol_by_volume': 0.0,
                           u'barcode': u'7610827921858',
                           u'country': u'CH',
                           u'created_at': u'2016-07-11T17:15:07.621Z',
                           u'display_name_translations': {u'de': u'coop FINE FOOD Erdn\xfcsse ger\xf6stet, mit Wasabi',
                                                          u'en': u'coop FINE FOOD Erdn\xfcsse ger\xf6stet, mit Wasabi',
                                                          u'fr': u'coop FINE FOOD Cacahu\xe8tes grill\xe9es au wasabi',
                                                          u'it': u'coop FINE FOOD Arachidi tostate al wasabi'},
                           u'id': 2357,
                           u'images': [{u'categories': [],
                                        u'large': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10169/large_7610827921858.jpg?v=1490486417',
                                        u'medium': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10169/medium_7610827921858.jpg?v=1490486417',
                                        u'thumb': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10169/thumb_7610827921858.jpg?v=1490486417',
                                        u'xlarge': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10169/xlarge_7610827921858.jpg?v=1490486417'},
                                       {u'categories': [],
                                        u'large': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10168/large_7610827921858.jpg?v=1490486417',
                                        u'medium': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10168/medium_7610827921858.jpg?v=1490486417',
                                        u'thumb': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10168/thumb_7610827921858.jpg?v=1490486417',
                                        u'xlarge': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10168/xlarge_7610827921858.jpg?v=1490486417'},
                                       {u'categories': [],
                                        u'large': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10167/large_7610827921858.jpg?v=1490486417',
                                        u'medium': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10167/medium_7610827921858.jpg?v=1490486417',
                                        u'thumb': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10167/thumb_7610827921858.jpg?v=1490486417',
                                        u'xlarge': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10167/xlarge_7610827921858.jpg?v=1490486417'},
                                       {u'categories': [],
                                        u'large': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10166/large_7610827921858.jpg?v=1490486417',
                                        u'medium': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10166/medium_7610827921858.jpg?v=1490486417',
                                        u'thumb': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10166/thumb_7610827921858.jpg?v=1490486417',
                                        u'xlarge': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10166/xlarge_7610827921858.jpg?v=1490486417'},
                                       {u'categories': [],
                                        u'large': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10164/large_7610827921858.jpg?v=1490486417',
                                        u'medium': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10164/medium_7610827921858.jpg?v=1490486417',
                                        u'thumb': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10164/thumb_7610827921858.jpg?v=1490486417',
                                        u'xlarge': u'https://d2v5oodgkvnw88.cloudfront.net/uploads_production/image/data/10164/xlarge_7610827921858.jpg?v=1490486417'}],
                           u'ingredients_translations': {
                               u'de': u'Erdn\xfcsse, Getreidemehle (Weizen, Reis), Zucker, Wasabi 0.5 % (japanischer Meerrettich), modifizierte Maniokst\xe4rke (E 1404), Kartoffelst\xe4rke, Sojasauce (mit Weizen, Farbstoff [E 150d]), Reis\xf6l, Traubenzucker, Maltodextrin, Senfpulver, Farbstoffe (E 100, E 141).\r\nKochsalzgehalt insgesamt: 0.9 %.',
                               u'fr': u'cacahu\xe8tes, farines de c\xe9r\xe9ales (froment, riz), sucre, wasabi 0.5 % (raifort japonais), f\xe9cule de manioc modifi\xe9e (E 1404), f\xe9cule de pomme de terre, sauce au soja (avec froment, colorant [E 150d]), huile de riz, dextrose, maltodextrine, moutarde en poudre, colorants (E 100, E 141).\r\nTeneur totale en sel de cuisine: 0.9 %.'},
                           u'name_translations': {u'de': u'coop FINE FOOD Erdn\xfcsse ger\xf6stet, mit Wasabi',
                                                  u'fr': u'coop FINE FOOD Cacahu\xe8tes grill\xe9es au wasabi',
                                                  u'it': u'coop FINE FOOD Arachidi tostate al wasabi'},
                           u'nutrients': {u'carbohydrates': {u'name_translations': {u'de': u'Kohlenhydrate',
                                                                                    u'en': u'Carbohydrates',
                                                                                    u'fr': u'Glucides',
                                                                                    u'it': u'Carboidrati'},
                                                             u'per_day': None,
                                                             u'per_hundred': 31.0,
                                                             u'per_portion': None,
                                                             u'unit': u'g'},
                                          u'energy': {u'name_translations': {u'de': u'Energie',
                                                                             u'en': u'Energy',
                                                                             u'fr': u'\xc9nergie',
                                                                             u'it': u'Energia'},
                                                      u'per_day': None,
                                                      u'per_hundred': 2240.0,
                                                      u'per_portion': None,
                                                      u'unit': u'kJ'},
                                          u'energy_kcal': {u'name_translations': {u'de': u'Energie (kCal)',
                                                                                  u'en': u'Energy (kCal)',
                                                                                  u'fr': u'\xc9nergie (kCal)',
                                                                                  u'it': u'Energia (kCal)'},
                                                           u'per_day': None,
                                                           u'per_hundred': 536.0,
                                                           u'per_portion': None,
                                                           u'unit': u'kCal'},
                                          u'fat': {u'name_translations': {u'de': u'Fett',
                                                                          u'en': u'Fat',
                                                                          u'fr': u'Mati\xe8res grasses',
                                                                          u'it': u'Grassi'},
                                                   u'per_day': None,
                                                   u'per_hundred': 34.0,
                                                   u'per_portion': None,
                                                   u'unit': u'g'},
                                          u'protein': {u'name_translations': {u'de': u'Eiweiss',
                                                                              u'en': u'Protein',
                                                                              u'fr': u'Prot\xe9ines',
                                                                              u'it': u'Proteine'},
                                                       u'per_day': None,
                                                       u'per_hundred': 24.0,
                                                       u'per_portion': None,
                                                       u'unit': u'g'}},
                           u'origin_translations': {},
                           u'portion_quantity': 0.0,
                           u'portion_unit': u'g',
                           u'quantity': 150.0,
                           u'status': u'complete',
                           u'unit': u'g',
                           u'updated_at': u'2018-09-04T09:30:45.020Z'}],
                u'links': {},
                u'meta': {u'api_version': u'3.03', u'generated_in': 62}}

    return json.dumps(response)
