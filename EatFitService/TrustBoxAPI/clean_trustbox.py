from django.db.models import Q
from TrustBoxAPI.models import NutritionGroupAttribute, NutritionFact
import unicodedata
import re

def clean_nutrition_group_attribute():
    count = 0
    attributes = NutritionGroupAttribute.objects.filter()
    for attribute in attributes:
        value = attribute.value
        if not is_number(value):
            string_value = unicodedata.normalize('NFKD', value).encode('ascii','ignore')
            number = re.findall("\d+\.\d+", string_value)
            if len(number) == 0:
                number = int(filter(str.isdigit, str(string_value)))
            else:
                number = number[0]
            if is_number(number):
                attribute.value = str(number)
                attribute.save()
                count = count + 1
                print("saved: " + str(count))

def clean_nutrition_facts():
    count = 0
    attributes = NutritionFact.objects.filter(Q(canonical_name = "salt") | Q(canonical_name = "sodium"))
    for attribute in attributes:
        value = attribute.amount
        if value and not is_number(value):
            string_value = unicodedata.normalize('NFKD', value).encode('ascii','ignore')
            number = re.findall("\d+\.\d+", string_value)
            if len(number) == 0:
                number = re.findall("\d+\,\d+", string_value)
                if len(number) == 0:
                    try:
                        number = int(filter(str.isdigit, str(string_value)))
                    except:
                        number = "NONE"
                else:
                    number = number[0]
            else:
                number = number[0]
            if is_number(number):
                attribute.value = str(number)
                attribute.save()
                count = count + 1
                print("saved: " + str(count))


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
