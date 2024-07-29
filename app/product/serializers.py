from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Category, Product, ProductImage, ProductDiscount, Review


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""

    class Meta:
        model = Category
        fields = ("id", "name")


class ProductImageSerializer(serializers.ModelSerializer):
    """Product's image serializer"""

    class Meta:
        model = ProductImage
        fields = ("image",)


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer"""

    # Images related to the product
    images = ProductImageSerializer(many=True)
    # Price after discount
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "name",
            "description",
            "brand",
            "qty_in_stock",
            "properties",
            "rating",
            "price",
            "final_price",
            "discount",
            "images",
        )

    # Get price after discount using object's method
    # and set it for final_price field
    def get_final_price(self, obj):
        return obj.calculate_final_price()


class ProductDiscountSerializer(serializers.ModelSerializer):
    """Product discount serializer"""

    class Meta:
        model = ProductDiscount
        fields = (
            "id",
            "name",
            "description",
            "discount_percent",
            "start_date",
            "end_date",
            "is_active",
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer"""

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "product",
            "rating",
            "text",
            "updated_at",
        )
        read_only_fields = ("id", "user", "product")

    # Handle `unique_user_product_review` constraint violation
    def create(self, validated_data):
        this_user = self.context.get("request").user
        product_id = self.context["views"].kwargs.get("product_pk")
        # Error if the user tries to create another review for the same product
        if Review.objects.filter(user=this_user, product=product_id):
            error = "You have already written a review for this product!"
            raise ValidationError({"detail": error})

        return super().create(validated_data)
