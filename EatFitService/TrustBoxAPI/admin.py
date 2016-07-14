from django.contrib import admin

from TrustBoxAPI.models import Product, ImportLog, Nutrition, NutritionAttribute, NutritionFact, NutritionFactsGroup, NutritionLabel, NutritionGroupAttribute, ProductAttribute, ProductName, NwdMainCategory, NwdSubcategory, MissingTrustboxItem

class MissingTrustboxItemAdmin(admin.ModelAdmin):
    list_display = ("name", "gtin", "total_weight")
    search_fields = ('name', 'gtin')
    save_as = True

admin.site.register(Product)
admin.site.register(ImportLog)
admin.site.register(Nutrition)
admin.site.register(NutritionAttribute)
admin.site.register(NutritionFact)
admin.site.register(NutritionFactsGroup)
admin.site.register(NutritionGroupAttribute)
admin.site.register(ProductAttribute)
admin.site.register(ProductName)
admin.site.register(NwdMainCategory)
admin.site.register(NwdSubcategory)
admin.site.register(NutritionLabel)
admin.site.register(MissingTrustboxItem, MissingTrustboxItemAdmin)
