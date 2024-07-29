from django.dispatch import receiver
from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from .models import Review


@receiver([post_save, post_delete], sender=Review)
def update_product_rating(sender, instance, **kwargs):
    """
    Update the product rating whenever a review for it saved or deleted
    """
    product = instance.product
    reviews = product.reviews.all()

    if reviews:
        avg_rating_dict = reviews.aggregate(Avg("rating"))
        avg_rating = avg_rating_dict["rating__avg"]
        product.rating = avg_rating
    else:
        product.rating = 0

    product.save()
