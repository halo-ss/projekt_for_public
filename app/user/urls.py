from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterUserView,
    ObtainTokenView,
    ProfileCRUDView,
    AddressCRUDView,
    CredentialsReadUpdateView,
    UserReadDeleteView,
    WhishItemListView,
    WishItemDetailView,
    CartDetailView,
    CartItemViewSet,
)

app_name = "user"

router = DefaultRouter()
router.register("cart-items", CartItemViewSet, "cart-item")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "me/wishitems/<int:pk>/", WishItemDetailView.as_view(), name="wishitem-detail"
    ),
    path("me/wishitems/", WhishItemListView.as_view(), name="wishitem-list"),
    path("me/shipping-address/", AddressCRUDView.as_view(), name="shipping-address"),
    path("me/profile/", ProfileCRUDView.as_view(), name="profile"),
    path(
        "me/credentials/",
        CredentialsReadUpdateView.as_view(),
        name="credentials",
    ),
    path("me/", UserReadDeleteView.as_view(), name="user-details"),
    path("cart/", CartDetailView.as_view(), name="cart"),
    path("token/", ObtainTokenView.as_view(), name="token"),
    path("register/", RegisterUserView.as_view(), name="register"),
]
