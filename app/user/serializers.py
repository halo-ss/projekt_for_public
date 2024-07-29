from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import authenticate
from .models import ShippingAddress, Profile, WishItem, Cart, CartItem
from product.models import Product


class AuthTokenSeralizer(serializers.Serializer):
    """Serializer for authentication token"""

    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False)

    def validate(self, attrs):
        # Ensure the credentials match to user
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(username=email, password=password)

        # If there's no mathcing user return error
        if not user:
            raise serializers.ValidationError("Incorrect credentials!")

        # If the user exists add him to validated data
        attrs["user"] = user
        return attrs


class ShippingAddressSerializer(serializers.ModelSerializer):
    """Customers's shipping address serializer"""

    class Meta:
        model = ShippingAddress
        fields = (
            "user",
            "country",
            "city",
            "street",
            "house",
            "apartment",
            "postal_code",
            "latitude",
            "longtitude",
        )
        read_only_fields = ("user",)


class ProfileSerializer(serializers.ModelSerializer):
    """Customer profile serializer"""

    class Meta:
        model = Profile
        fields = (
            "user",
            "first_name",
            "last_name",
            "telephone",
            "profile_photo",
        )
        read_only_fields = ("user",)


class UserRegisterSerializer(serializers.ModelSerializer):
    """User credentials serializer for register"""

    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password")
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class UserSerializer(UserRegisterSerializer):
    """Detailed user serializer"""

    profile = ProfileSerializer()
    shipping_address = ShippingAddressSerializer()

    class Meta(UserRegisterSerializer.Meta):
        fields = UserRegisterSerializer.Meta.fields + ("profile", "shipping_address")


class WishItemSerializer(serializers.ModelSerializer):
    """Wish item serializer"""

    class Meta:
        model = WishItem
        fields = ("id", "user", "product")
        read_only_fields = ("id", "user")

    def create(self, validated_data):
        this_user = self.context.get("request").user
        product = self.validated_data.get("product")

        # Error if the user tries to wish the same product again
        if WishItem.objects.filter(user=this_user, product=product):
            error = "You have already wished this product!"
            raise ValidationError({"detail": error})

        return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    """Cart serializer for reading"""

    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("user", "total_amount")

    def get_total_amount(self, obj):
        return obj.get_total_amount()


class CartItemSerializer(serializers.ModelSerializer):
    """Cart item serializer for CRD operations"""

    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ("id", "cart", "product", "quantity", "total_cost")
        read_only_fields = ("id", "cart")

    def get_total_cost(self, obj):
        return obj.get_total_cost()

    def validate(self, attrs):
        # Validation for create operation
        if not self.instance:
            self._validate_unique_cart_product(attrs)
            self._validate_quantity_in_stock(attrs)
        # Validation for update operation
        else:
            self._validate_quantity_in_stock(attrs, is_update=True)

        return attrs

    def _validate_unique_cart_product(self, attrs):
        """Ensure the product is not already in the user's cart"""
        cart = self.context["request"].user.cart
        product = attrs.get("product")
        # Error if the user tries to add the same product to cart again
        if CartItem.objects.filter(cart=cart, product=product):
            error = "You have already added this item to your cart!"
            raise ValidationError({"detail": error})

    def _validate_quantity_in_stock(self, attrs, is_update=False):
        """Ensure `cart_item.quantity` doesn't exceed product's stock"""
        if not is_update:
            product = attrs.get("product")
            quantity = attrs.get("quantity")
        else:
            # Use `product` of existing cart item when update
            product = self.instance.product
            # If `quantity` not provided when update action then
            # take existing quantity value
            quantity = attrs.get("quantity") or self.instance.quantity

        if quantity > product.qty_in_stock:
            error = f"Out of stock! ({quantity} > {product.qty_in_stock})"
            raise ValidationError(error)


class CartItemUpdateSerializer(CartItemSerializer):
    """Cart item serializer for update operations"""

    class Meta(CartItemSerializer.Meta):
        # Make `product` field uneditable
        read_only_fields = CartItemSerializer.Meta.read_only_fields + ("product",)
