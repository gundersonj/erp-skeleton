from django.urls import path
from .web_views import (
    CustomerListView, CustomerCreateView, CustomerUpdateView, CustomerDeleteView
)

app_name = "customers"

urlpatterns = [
    path("", CustomerListView.as_view(), name="list"),
    path("new/", CustomerCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", CustomerUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", CustomerDeleteView.as_view(), name="delete"),
]
