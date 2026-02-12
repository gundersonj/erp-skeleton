from rest_framework.routers import DefaultRouter

from customers.views import CustomerViewSet
from products.views import ProductViewSet
from orders.views import OrderViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="customer")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"order-items", OrderItemViewSet, basename="orderitem")

urlpatterns = router.urls
