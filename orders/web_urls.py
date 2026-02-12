from django.urls import path
from .web_views import OrderListView, OrderCreateView, OrderDetailView, OrderDeleteView

app_name = "orders"

urlpatterns = [
    path("", OrderListView.as_view(), name="list"),
    path("new/", OrderCreateView.as_view(), name="create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", OrderDeleteView.as_view(), name="delete"),
]
