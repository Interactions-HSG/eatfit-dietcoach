from modeltranslation.translator import translator, TranslationOptions
from api.models import AvatarTip
from api.models import AvatarMessage
from api.models import FoodItem, FoodItemSupplement, Category, ShoppingTip

class FoodItemTranslationOptions(TranslationOptions):
    fields = ('name', 'tooltip', "unit")

class FoodItemSupplementTranslationOptions(TranslationOptions):
    fields = ('name', "unit")

class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'category_detail_text')

class ShoppingTipsTranslationOptions(TranslationOptions):
    fields = ('text',)

class AvatarMessageTranslationOptions(TranslationOptions):
    fields = ("message",)

class AvatarTipsTranslationOptions(TranslationOptions):
    fields = ("message",)

translator.register(FoodItem, FoodItemTranslationOptions)
translator.register(FoodItemSupplement, FoodItemSupplementTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
translator.register(ShoppingTip, ShoppingTipsTranslationOptions)
translator.register(AvatarMessage, AvatarMessageTranslationOptions)
translator.register(AvatarTip, AvatarTipsTranslationOptions)