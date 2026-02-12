from django.urls import path
from .web_views import (
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, product_price
)

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="list"),
    path("new/", ProductCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", ProductUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ProductDeleteView.as_view(), name="delete"),
    path("<int:pk>/price/", product_price, name="price"),
]