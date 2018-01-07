from django.contrib import admin
from NutritionService.models import MajorCategory, Product, MinorCategory

class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_name_de", "gtin")
    search_fields = ('product_name_de', 'gtin')
    save_as = True

admin.site.register(Product, ProductAdmin)
admin.site.register(MajorCategory)
admin.site.register(MinorCategory)
