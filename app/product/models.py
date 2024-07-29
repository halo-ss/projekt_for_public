import os
from datetime import date
from uuid import uuid4
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


def generate_product_image_path(instance, filename):
    """Generate product image path with unique filename"""
    extension = os.path.splitext(filename)[1]
    filename = f"{uuid4()}{extension}"
    return os.path.join("uploads", "product", filename)


def validate_unique_keys(value):
    """Check if product property keys are unique"""
    keys = [k.lower() for k in value]
    if len(keys) != len(set(keys)):
        duplicating_keys = set([k for k in keys if keys.count(k) > 1])
        raise ValidationError(f"Property key duplication: {duplicating_keys}")


class Category(models.Model):
    """Product's category model"""

    name = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model"""

    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=100, blank=True)
    qty_in_stock = models.IntegerField(
        verbose_name="Количество на складе",
        validators=[MinValueValidator(0)],
    )
    # TODO: Make more user friendly input in admin panel
    properties = models.JSONField(
        blank=True,
        default=dict,
        validators=[validate_unique_keys],
        verbose_name="Дополнительные свойства",
    )
    rating = models.FloatField(
        blank=True,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )
    discount = models.ForeignKey(
        to="ProductDiscount",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def calculate_final_price(self):
        """Get the price after discount"""
        if self.discount and self.discount.is_current():
            discount_amount = (self.price / 100) * self.discount.discount_percent
            return round((self.price - discount_amount), 2)

        return self.price


class ProductImage(models.Model):
    """Product's image model"""

    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        upload_to=generate_product_image_path,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProductDiscount(models.Model):
    """Product' discount model"""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    discount_percent = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    start_date = models.DateField(default=date.today)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_current(self):
        """Check if the discount is currently active"""
        today = date.today()
        return self.is_active and self.start_date <= today < self.end_date


class Review(models.Model):
    """Review model"""

    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # Restrict a user to write more than 1 review per product
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product_review"
            )
        ]
