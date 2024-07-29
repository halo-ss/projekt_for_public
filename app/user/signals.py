from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from .models import Cart, CartItem


@receiver(post_save, sender=get_user_model())
def create_cart_for_user(sender, instance, created, **kwargs):
    """Create a cart for the new user"""
    if created:
        Cart.objects.create(user=instance)
