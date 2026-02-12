from decimal import Decimal
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError

from products.models import Product
from customers.models import Customer
from orders.models import Order, OrderItem


class OrderTotalsTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Acme")
        self.p1 = Product.objects.create(sku="SKU-1", name="Widget", price=Decimal("10.00"))
        self.p2 = Product.objects.create(sku="SKU-2", name="Gadget", price=Decimal("2.50"))

    def test_line_total(self):
        order = Order.objects.create(customer=self.customer)
        item = OrderItem.objects.create(
            order=order,
            product=self.p1,
            quantity=3,
            unit_price=Decimal("10.00"),
        )
        self.assertEqual(item.line_total(), Decimal("30.00"))

    def test_order_subtotal_and_total_items(self):
        order = Order.objects.create(customer=self.customer)
        OrderItem.objects.create(order=order, product=self.p1, quantity=2, unit_price=Decimal("10.00"))
        OrderItem.objects.create(order=order, product=self.p2, quantity=4, unit_price=Decimal("2.50"))

        self.assertEqual(order.total_items(), 6)
        self.assertEqual(order.subtotal(), Decimal("30.00"))


class OrdersWebViewTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Acme")
        self.product = Product.objects.create(sku="SKU-1", name="Widget", price=Decimal("10.00"))

    def test_orders_list_page_loads(self):
        resp = self.client.get(reverse("orders:list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Orders")

    def test_create_order_redirects_to_detail(self):
        resp = self.client.post(
            reverse("orders:create"),
            data={"customer": self.customer.id, "status": "DRAFT"},
        )
        self.assertEqual(resp.status_code, 302)

        order = Order.objects.get()
        self.assertRedirects(resp, reverse("orders:detail", kwargs={"pk": order.pk}))

    def test_add_line_item_via_formset_on_detail_post(self):
        order = Order.objects.create(customer=self.customer)
        url = reverse("orders:detail", kwargs={"pk": order.pk})

        post_data = {
            "items-TOTAL_FORMS": "1",
            "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0",
            "items-MAX_NUM_FORMS": "1000",
            "items-0-product": str(self.product.pk),
            "items-0-quantity": "3",
            "items-0-unit_price": "10.00",
        }

        resp = self.client.post(url, data=post_data)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, url)

        order.refresh_from_db()
        self.assertEqual(order.items.count(), 1)

        item = order.items.first()
        self.assertEqual(item.product_id, self.product.id)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.unit_price, Decimal("10.00"))

        self.assertEqual(item.line_total(), Decimal("30.00"))
        self.assertEqual(order.subtotal(), Decimal("30.00"))
        self.assertEqual(order.total_items(), 3)


class OrdersApiTests(TestCase):
    def setUp(self):
        self.api = APIClient()

        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
            is_staff=True,
            is_superuser=True,
        )
        
        self.api.force_authenticate(user=self.user)

        self.customer = Customer.objects.create(name="Acme")
        self.product = Product.objects.create(sku="SKU-1", name="Widget", price=Decimal("10.00"))

    def test_create_order_via_api(self):
        resp = self.api.post(
            "/api/orders/",
            {"customer": self.customer.id, "status": "DRAFT"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)

    def test_create_order_item_via_api(self):
        order = Order.objects.create(customer=self.customer)

        resp = self.api.post(
            "/api/order-items/",
            {"order": order.id, "product": self.product.id, "quantity": 2, "unit_price": "10.00"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)

        order.refresh_from_db()
        self.assertEqual(order.items.count(), 1)


class DeleteBehaviorTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Acme")
        self.product = Product.objects.create(sku="SKU-1", name="Widget", price=Decimal("10.00"))
        self.order = Order.objects.create(customer=self.customer)
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            unit_price=Decimal("10.00"),
        )

    def test_delete_order_cascades_items(self):
        self.order.delete()
        self.assertEqual(OrderItem.objects.count(), 0)

    def test_delete_product_is_protected(self):
        with self.assertRaises(ProtectedError):
            self.product.delete()

    def test_delete_customer_is_protected(self):
        with self.assertRaises(ProtectedError):
            self.customer.delete()
