from django.contrib import admin
from NutritionService.models import MajorCategory, Product, MinorCategory, Allergen, NutritionFact

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


admin.site.register(Product, ProductAdmin)
admin.site.register(MajorCategory)
admin.site.register(MinorCategory)
