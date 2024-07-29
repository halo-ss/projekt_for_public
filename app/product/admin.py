from django.contrib import admin
from .models import Category, Product, ProductImage, ProductDiscount, Review


class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "get_final_price", "qty_in_stock", "rating")

    # Calculate dynamic field `get_final_price`
    def get_final_price(self, obj):
        return obj.calculate_final_price()

    # Set verbose name for dynamic field `get_final_price`
    get_final_price.short_description = "Итоговая цена"


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductDiscount)
admin.site.register(Review)
