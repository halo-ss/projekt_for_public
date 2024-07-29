from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator


class Order(models.Model):
    """Order model"""

    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(
        to="user.ShippingAddress",
        on_delete=models.SET_NULL,
        null=True,
    )
    total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )
    is_paid = models.BooleanField(default=False, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    """Cart item model"""

    order = models.ForeignKey(
        to=Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(to="product.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_cost(self):
        """
        Get the total cost of the order item taking into account
        its quantity and discount.
        """
        return round(self.product.calculate_final_price() * self.quantity, 2)

    class Meta:
        constraints = [
            # Restrict adding the same product to order again
            models.UniqueConstraint(
                fields=["order", "product"], name="unique_order_product"
            )
        ]


class Payment(models.Model):
    """Payment model"""

    # Payment status choices
    PENDING = "P"
    SUCCEEDED = "S"
    CANCELED = "C"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (SUCCEEDED, "Succeeded"),
        (CANCELED, "Canceled"),
    )

    order = models.OneToOneField(to=Order, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )
    currency = models.CharField(max_length=3, default="RUB")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
