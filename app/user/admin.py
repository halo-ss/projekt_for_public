from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Profile, ShippingAddress, WishItem, Cart, CartItem


admin.site.register(get_user_model())
admin.site.register(Profile)
admin.site.register(ShippingAddress)
admin.site.register(WishItem)
admin.site.register(Cart)
admin.site.register(CartItem)
