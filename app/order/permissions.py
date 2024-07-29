import ipaddress
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from .models import Order


class DoesUserHaveAddress(BasePermission):
    """Allow access only to user with shipping address"""

    message = "User must have an address to make orders!"

    def has_permission(self, request, view):
        shipping_address = getattr(request.user, "shipping_address", None)
        if not shipping_address:
            return False
        return True


class IsCartNotEmpty(BasePermission):
    """Allow access only to user with items in cart"""

    message = "Your cart is empty!"

    def has_permission(self, request, view):
        if not request.user.cart.cart_items.all():
            return False
        return True


class IsOrderNotPaid(BasePermission):
    """Allow acces only if the order is not paid"""

    message = "This order is already paid!"

    def has_permission(self, request, view):
        order_id = view.kwargs.get("order_pk")
        order = get_object_or_404(Order, pk=order_id)
        if order.is_paid:
            return False
        return True


class IsAllowedIP(BasePermission):
    """Allow access only to allowed list of IPs"""

    message = "Your IP address is not allowed!"

    YOOKASSA_IP_ADDRESSES = [
        "185.71.76.0/27",
        "185.71.77.0/27",
        "77.75.153.0/25",
        "77.75.156.11",
        "77.75.156.35",
        "77.75.154.128/25",
        "2a02:5180::/32",
    ]

    def has_permission(self, request, view):
        # If X-Forwarded-For header is present, extract the IP from it
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            # It may contain a list of IPs, take the first one
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            # If no x_forwarder_for take REMOTE_ADDR
            ip = request.META.get("REMOTE_ADDR")

        return any(
            ipaddress.ip_address(ip) in ipaddress.ip_network(net)
            for net in self.YOOKASSA_IP_ADDRESSES
        )
