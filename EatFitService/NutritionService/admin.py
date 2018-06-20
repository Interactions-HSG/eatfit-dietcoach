from django.contrib import admin
from NutritionService.models import MajorCategory, Product, MinorCategory, Allergen, NutritionFact, ErrorLog, \
                                    CrowdsourceProduct, NotFoundLog, HealthTipp, NutrientName


class AllergenInline(admin.TabularInline):
    model = Allergen


class NutrientInline(admin.TabularInline):
    model = NutritionFact


class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_name_de", "gtin")
    search_fields = ('product_name_de', 'gtin')
    save_as = True
    inlines = [
        AllergenInline,
        NutrientInline
    ]

class NotFoundLogAdmin(admin.ModelAdmin):
    list_display = ("gtin", "count", "first_searched_for")
    search_fields = ("gtin", "count", "first_searched_for")


admin.site.register(Product, ProductAdmin)
admin.site.register(MajorCategory)
admin.site.register(MinorCategory)
admin.site.register(ErrorLog)
admin.site.register(HealthTipp)
admin.site.register(NutrientName)
admin.site.register(CrowdsourceProduct)
admin.site.register(NotFoundLog, NotFoundLogAdmin)