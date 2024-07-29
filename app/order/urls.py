from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, PaymentCreateView, YookassaWebhookView

app_name = "order"

router = DefaultRouter()
router.register("orders", OrderViewSet)


urlpatterns = [
    path(
        "orders/<int:order_pk>/create-payment/",
        PaymentCreateView.as_view(),
        name="create-payment",
    ),
    path("", include(router.urls)),
    path("yookassa-webhooks/", YookassaWebhookView.as_view(), name='yookassa-webhooks'),
]
