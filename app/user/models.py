import os
from uuid import uuid4
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def generate_user_image_path(instance, filename):
    """Generate user image path with unique uuid filename"""
    extension = os.path.splitext(filename)[1]
    filename = f"{uuid4()}{extension}"
    return os.path.join("uploads", "user", filename)


class UserManager(BaseUserManager):
    """User model manager"""

    def create_user(self, email, password=None, **fields):
        user = self.model(
            email=self.normalize_email(email),
            **fields,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **fields):
        superuser = self.model(
            email=self.normalize_email(email),
            **fields,
        )
        superuser.set_password(password)
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save()
        return superuser


# TODO: Replace with `AbstractUser` to ensure correct password encryption
# when creating users via admin panel
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    objects = UserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    """User's profile model"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=70, blank=True)
    last_name = models.CharField(max_length=70, blank=True)
    telephone = models.CharField(max_length=50, unique=True)
    profile_photo = models.ImageField(
        upload_to=generate_user_image_path, blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ShippingAddress(models.Model):
    """User's shipping address"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="shipping_address",
    )
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    house = models.CharField(max_length=30)
    apartment = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=30)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longtitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WishItem(models.Model):
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey(to="product.Product", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # Prohibit a user to wish the same product again
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_user_product"
            )
        ]


class Cart(models.Model):
    """User's cart model"""

    user = models.OneToOneField(
        to=get_user_model(),
        on_delete=models.CASCADE,
        primary_key=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_amount(self):
        """Get total amount for all cart items"""
        total_amount = sum(item.get_total_cost() for item in self.cart_items.all())
        return round(total_amount, 2)


class CartItem(models.Model):
    """Cart item model"""

    cart = models.ForeignKey(
        to=Cart, on_delete=models.CASCADE, related_name="cart_items"
    )
    product = models.ForeignKey(to="product.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_cost(self):
        """
        Get the total cost of the cart item taking into account
        its quantity and discount.
        """
        return round(self.product.calculate_final_price() * self.quantity, 2)

    class Meta:
        constraints = [
            # Restrict a user to add the same product to the cart again
            models.UniqueConstraint(
                fields=["cart", "product"], name="unique_cart_product"
            ),
        ]

    def clean(self):
        # Validate the quantity does not exceed product's stock
        if self.quantity > self.product.qty_in_stock:
            raise ValidationError(
                f"You cannot buy more than we have! ({self.quantity} > {self.product.qty_in_stock})"
            )

    def save(self, *args, **kwargs):
        # Call clean to enforce validation
        self.clean()
        super().save(*args, **kwargs)
