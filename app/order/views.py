import uuid, yookassa
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Order, Payment
from .serializers import (
    OrderSerializer,
    YookassaPaymentRequestSerializer,
    YookassaPaymentResponseSerializer,
)
from .permissions import (
    DoesUserHaveAddress,
    IsCartNotEmpty,
    IsOrderNotPaid,
    IsAllowedIP,
)


# Set Yookassa credentials
yookassa.Configuration.account_id = settings.YOOKASSA_ACCOUNT_ID
yookassa.Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


class OrderViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    """Manage CRD ops on order"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["created_at"]
    filterset_fields = ["is_paid"]

    def get_queryset(self):
        # Limit orders to this user
        queryset = self.queryset.filter(user=self.request.user)
        # Allow to delete/cancel only not paid orders
        if self.action == "destroy":
            return queryset.filter(is_paid=False)
        return queryset

    def get_permissions(self):
        # Require address and cart items for order creation
        if self.action == "create":
            return [permission() for permission in self.permission_classes] + [
                DoesUserHaveAddress(),
                IsCartNotEmpty(),
            ]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = self.request.user
        # Set default values for order
        return serializer.save(
            user=user,
            shipping_address=user.shipping_address,
            total=user.cart.get_total_amount(),
        )


class PaymentCreateView(APIView):
    """Create Yookassa payment object and Payment model instance"""

    permission_classes = [IsAuthenticated, IsOrderNotPaid]
    authentication_classes = [TokenAuthentication]
    serializer_class = YookassaPaymentRequestSerializer

    @extend_schema(
        # Change serializer for responses
        responses=YookassaPaymentResponseSerializer,
    )
    def post(self, request, order_pk):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return_url = serializer.validated_data.get("return_url")
        # Limit orders to this user so the user can pay only for his orders
        user_orders = Order.objects.filter(user=request.user)
        order = get_object_or_404(user_orders, pk=order_pk)
        # Create Yookassa payment object
        payment = yookassa.Payment.create(
            {
                # TODO: include commission to amount
                "amount": {
                    "value": order.total,
                    "currency": "RUB",
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url,
                },
                "capture": True,
                "description": f"Оплата заказа №{order.id} для {order.user.email}",
                "metadata": {"order_id": order.id},
            },
            uuid.uuid4(),
        )

        yookassa_confirmation_url = YookassaPaymentResponseSerializer(
            payment.confirmation
        ).data

        # Delete existing pending payment for the order, if present
        if Payment.objects.filter(order=order):
            Payment.objects.filter(order=order).delete()
        # Create Payment model instance
        Payment.objects.create(order=order, amount=order.total)
        return Response(yookassa_confirmation_url, status=201)


class YookassaWebhookView(APIView):
    """Modify order and payment based on the payment status"""

    permission_classes = [IsAllowedIP]

    def post(self, request):
        order_id = request.data["object"]["metadata"]["order_id"]
        order = get_object_or_404(Order, pk=order_id)
        payment = get_object_or_404(Payment, order=order)

        # Mark payment and order as succeeded if payment succeeded
        if request.data["event"] == "payment.succeeded":
            payment.status = payment.SUCCEEDED
            payment.payment_method = request.data["object"]["payment_method"]["type"]
            order.is_paid = True
        # Mark payment  as canceled if payment canceled
        elif request.data["event"] == "payment.canceled":
            payment.status = payment.CANCELED

        payment.save()
        order.save()

        return Response(status=200)
