from rest_framework import generics, permissions, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    AuthTokenSeralizer,
    ShippingAddressSerializer,
    ProfileSerializer,
    WishItemSerializer,
    CartSerializer,
    CartItemSerializer,
    CartItemUpdateSerializer,
)
from .models import Profile, ShippingAddress, WishItem, CartItem


class RegisterUserView(CreateAPIView):
    """Manage user creation"""

    serializer_class = UserRegisterSerializer


class ObtainTokenView(ObtainAuthToken):
    """Manage auth token creation and obtaining"""

    serializer_class = AuthTokenSeralizer


class UserReadDeleteView(
    generics.RetrieveAPIView,
    generics.DestroyAPIView,
):
    """Manage retrieving full user data and deleting him"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class CredentialsReadUpdateView(
    generics.RetrieveAPIView,
    generics.UpdateAPIView,
):
    """Manage Read and Update operations on user's credentials"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserRegisterSerializer

    def get_object(self):
        return self.request.user


class AddressCRUDView(
    generics.CreateAPIView,
    generics.RetrieveAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView,
):
    """Manage CRUD operations on user's shipping address"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ShippingAddressSerializer

    def get_object(self):
        # Make accessing a non-existent object produce an error
        try:
            return self.request.user.shipping_address
        except ShippingAddress.DoesNotExist:
            raise NotFound({"detail": "Not found."})

    def perform_create(self, serializer):
        # Set user field to this user by default
        return serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Report that user can have only one shipping address
        if getattr(request.user, "shipping_address", None):
            return Response(
                {"detail": "User can have only 1 shipping address!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)


class ProfileCRUDView(
    generics.CreateAPIView,
    generics.RetrieveAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView,
):
    """Manage CRUD operations on user's profile"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = ProfileSerializer

    def get_object(self):
        # Make accessing a non-existent object produce an error
        try:
            return self.request.user.profile
        except Profile.DoesNotExist:
            raise NotFound({"detail": "Not found."})

    def perform_create(self, serializer):
        # Set user field to this user by default
        return serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Report that user can have only one profile
        if getattr(request.user, "profile", None):
            return Response(
                {"detail": "This user already has a profile!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)


class WhishItemMixin:
    """Basic features for whish item views"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = WishItem.objects.all()
    serializer_class = WishItemSerializer

    def get_queryset(self):
        # Limit whishes to the current user
        return self.queryset.filter(user=self.request.user)


class WhishItemListView(WhishItemMixin, generics.ListCreateAPIView):
    """Manage wish item create, list ops"""

    def perform_create(self, serializer):
        # Set `user` to this user
        return serializer.save(user=self.request.user)


class WishItemDetailView(WhishItemMixin, generics.RetrieveDestroyAPIView):
    """Manage wish item retrieve, destroy ops"""

    pass


class CartDetailView(generics.RetrieveAPIView):
    """Manage user's cart retrieving"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = CartSerializer

    def get_object(self):
        return self.request.user.cart


class CartItemViewSet(viewsets.ModelViewSet):
    """Manage CRUD operations on cart items"""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        # Limit cart items to this user's cart
        return self.queryset.filter(cart=self.request.user.cart)

    def get_serializer_class(self):
        # Use serializer with uneditable `product` field when update action
        if self.action in ["update", "partial_update"]:
            return CartItemUpdateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        # Assign cart items to this user's cart
        return serializer.save(cart=self.request.user.cart)
