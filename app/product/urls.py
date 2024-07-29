from drf_spectacular.utils import extend_schema
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ProductDiscountViewSet,
    ReviewListView,
    ReviewDetailView,
)


app_name = "product"

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)
router.register("discounts", ProductDiscountViewSet)


def add_tags(view, tags):
    """Add OpenAPI tags to a view for schema generation."""
    view._schema = extend_schema(tags=tags)(view)
    return view.as_view()


urlpatterns = [
    path("", include(router.urls)),
    path(
        "products/<int:product_pk>/reviews/",
        # Add tags to recognize this url as `reviews` recource
        add_tags(ReviewListView, tags=["reviews"]),
        name="review-list",
    ),
    path("reviews/<int:pk>/", ReviewDetailView.as_view(), name="review-detail"),
]
