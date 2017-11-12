from django.contrib import admin
from api.models import AvatarTip
from adminsortable.admin import SortableAdmin

from api.models import SaltTrackerUser, Category, FoodItem, FoodRecord, ProfileData, ReebateCredentials, MigrosItem, ShoppingTip, FoodItemSupplement,AutoidScraperMigrosItem, AvatarData, AvatarMessage, Study
from modeltranslation.admin import TranslationAdmin


class MigrosItemAdmin(admin.ModelAdmin):
    list_display = ("name","count", "gtin", "total_quantity")
    search_fields = ('name', 'gtin')

class FoodItemAdmin(TranslationAdmin, SortableAdmin):
    list_display = ("name","get_categroy_name")
    def get_categroy_name(self, obj):
        return obj.category.name
    get_categroy_name.short_description = 'Kategorie'
    get_categroy_name.admin_order_field = 'category__name'

class CategoryAdmin(TranslationAdmin, SortableAdmin):
    pass

class FoodItemSupplementAdmin(TranslationAdmin):
    save_as = True

class AvatarMessageAdmin(SortableAdmin):
    pass

admin.site.register(SaltTrackerUser)
admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
admin.site.register(FoodRecord)
admin.site.register(ProfileData)
admin.site.register(ReebateCredentials)
admin.site.register(AutoidScraperMigrosItem, MigrosItemAdmin)
admin.site.register(ShoppingTip)
admin.site.register(FoodItemSupplement, FoodItemSupplementAdmin)
admin.site.register(AvatarData)
admin.site.register(AvatarMessage, AvatarMessageAdmin)
admin.site.register(AvatarTip)
admin.site.register(Study)
