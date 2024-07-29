from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import OrderItem, Order
from product.models import Product


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer"""

    class Meta:
        model = Order
        fields = ("id", "user", "shipping_address", "total", "is_paid")
        read_only_fields = ("id", "user", "shipping_address", "total", "is_paid")


class YookassaPaymentRequestSerializer(serializers.Serializer):
    """Serializer for yookassa payment creation"""

    return_url = serializers.URLField()


class YookassaPaymentResponseSerializer(serializers.Serializer):
    """Serializer for confirmation url return"""

    confirmation_url = serializers.URLField()
