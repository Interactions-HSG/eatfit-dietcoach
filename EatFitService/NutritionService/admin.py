from django.contrib import admin
from django.utils.functional import curry
from django.contrib import messages
from NutritionService.views.crowdsource_views import __create_products_from_crowdsource
from NutritionService.models import MajorCategory, Product, MinorCategory, Allergen, NutritionFact, ErrorLog, \
                                    CrowdsourceProduct, NotFoundLog, HealthTipp, NutrientName, \
                                    ReceiptToNutritionPartner, ReceiptToNutritionUser, Matching, DigitalReceipt, \
                                    Retailer, MarketRegion, AdditionalImage, ImportErrorLog

nutrients_to_prefill = ["energyKcal", "energyKJ", "protein", "salt", "sodium", "dietaryFiber", "saturatedFat", "sugars",
                        "totalCarbohydrate", "totalFat"]
allergens_to_fill = ["allergenEggs",
                     "allergenGluten",
                     "allergenMilk",
                     "allergenSoy",
                     "allergenTreeNuts",
                     "allergenPeanuts",
                     "allergenSulphites",
                     "allergenMustard",
                     "allergenSesameSeeds",
                     "allergenCellery",
                     "allergenFish",
                     "allergenLupin",
                     "allergenCrustacean",
                     "allergenMolluscs"]


class AllergenInline(admin.TabularInline):
    model = Allergen
    extra = 14

    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        if not obj and request.method == "GET":
            for allergen in allergens_to_fill:
                initial.append({'name': allergen })
        formset = super(AllergenInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset


class NutrientInline(admin.TabularInline):
    model = NutritionFact
    extra = 10
    
    def get_formset(self, request, obj=None, **kwargs):
            initial = []
            if not obj and request.method == "GET":
                for nutrient in nutrients_to_prefill:
                    unit_of_measure = 'g'
                    if "Kcal" in nutrient:
                        unit_of_measure = "Kcal"
                    elif "KJ" in nutrient:
                        unit_of_measure = "KJ"
                    initial.append({'name': nutrient, 'unit_of_measure': unit_of_measure })
            formset = super(NutrientInline, self).get_formset(request, obj, **kwargs)
            formset.__init__ = curry(formset.__init__, initial=initial)
            return formset


class RetailerInline(admin.TabularInline):
    model = Retailer
    extra = 5


class MarketRegionInline(admin.TabularInline):
    model = MarketRegion
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_name_de", "gtin")
    search_fields = ('product_name_de', 'gtin')
    save_as = True
    inlines = [
        AllergenInline,
        NutrientInline,
        RetailerInline,
        MarketRegionInline
    ]


class NotFoundLogAdmin(admin.ModelAdmin):
    list_display = ("gtin", "count", "first_searched_for")
    search_fields = ("gtin", "count", "first_searched_for")


class MatchingAdmin(admin.ModelAdmin):
    list_display = ("gtin", "article_id", "article_type")
    search_fields = ("gtin", "article_id", "article_type")

    
def approve_crowdsource_product(self, request, queryset):
    success, errors, invalid_gtins = __create_products_from_crowdsource(list(queryset))
    if success:
        message = "Products successfully converted"
        self.message_user(request, message, level=messages.INFO)
    else:
        invalid_gtins_message = ""
        for gtin in invalid_gtins:
            invalid_gtins_message  = invalid_gtins_message + str(gtin["gtin"]) + ": " + ''.join(gtin["errors"]) + "\n"
        message = "Error converting products: " + errors + "\nInvalid GTINS: " + invalid_gtins_message
        self.message_user(request, message, level=messages.ERROR)


class CrowdsourceProductAdmin(admin.ModelAdmin):
    list_display = ('name', )
    actions = [approve_crowdsource_product]


class DigitalReceiptAdmin(admin.ModelAdmin):
    list_display = ("article_id", "article_type", "business_unit")
    search_fields = ("article_id", "article_type", "business_unit")


class ReceiptToNutritionUserAdmin(admin.ModelAdmin):
    list_display = ("r2n_partner", "r2n_username", "r2n_user_active")
    search_fields = ("r2n_partner", "r2n_username", "r2n_user_active")


admin.site.register(Allergen)
admin.site.register(Product, ProductAdmin)
admin.site.register(MajorCategory)
admin.site.register(MinorCategory)
admin.site.register(ErrorLog)
admin.site.register(HealthTipp)
admin.site.register(NutrientName)
admin.site.register(CrowdsourceProduct, CrowdsourceProductAdmin)
admin.site.register(NotFoundLog, NotFoundLogAdmin)
admin.site.register(Matching, MatchingAdmin)
admin.site.register(ReceiptToNutritionPartner)
admin.site.register(ReceiptToNutritionUser, ReceiptToNutritionUserAdmin)
admin.site.register(DigitalReceipt, DigitalReceiptAdmin)
admin.site.register(AdditionalImage)
admin.site.register(ImportErrorLog)
