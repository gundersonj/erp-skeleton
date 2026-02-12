from decimal import Decimal
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError

from products.models import Product
from customers.models import Customer
from orders.models import Order, OrderItem


class ProductsWebViewTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            sku="SKU-1",
            name="Widget",
            price=Decimal("10.00"),
            is_active=True,
        )

    def test_products_list_page_loads(self):
        resp = self.client.get(reverse("products:list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Products")
        self.assertContains(resp, "SKU-1")

    def test_create_product(self):
        resp = self.client.post(
            reverse("products:create"),
            data={
                "sku": "SKU-2",
                "name": "Gadget",
                "price": "2.50",
                "is_active": "on",  # checkbox
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Product.objects.filter(sku="SKU-2").exists())

    def test_update_product(self):
        resp = self.client.post(
            reverse("products:update", kwargs={"pk": self.product.pk}),
            data={
                "sku": self.product.sku,
                "name": "Widget Updated",
                "price": "11.25",
                "is_active": "on",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Widget Updated")
        self.assertEqual(self.product.price, Decimal("11.25"))

    def test_delete_product(self):
        p = Product.objects.create(sku="DEL-1", name="Delete Me", price=Decimal("1.00"), is_active=True)
        resp = self.client.post(reverse("products:delete", kwargs={"pk": p.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=p.pk).exists())


class ProductsApiTests(TestCase):
    def setUp(self):
        self.api = APIClient()

        # If your API uses model perms/admin-only, make this a superuser.
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
            is_staff=True,
            is_superuser=True,
        )
        self.api.force_authenticate(user=self.user)

        self.product = Product.objects.create(
            sku="SKU-1",
            name="Widget",
            price=Decimal("10.00"),
            is_active=True,
        )

    def test_list_products(self):
        resp = self.api.get("/api/products/")
        self.assertEqual(resp.status_code, 200)
        data = resp.data["results"] if isinstance(resp.data, dict) and "results" in resp.data else resp.data
        self.assertGreaterEqual(len(data), 1)

    def test_create_product_via_api(self):
        resp = self.api.post(
            "/api/products/",
            {"sku": "SKU-2", "name": "Gadget", "price": "2.50", "is_active": True},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Product.objects.filter(sku="SKU-2").exists())

    def test_update_product_via_api(self):
        resp = self.api.patch(
            f"/api/products/{self.product.pk}/",
            {"price": "11.25"},
            format="json",
        )
        self.assertIn(resp.status_code, (200, 202))
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, Decimal("11.25"))

    def test_delete_product_via_api(self):
        p = Product.objects.create(sku="DEL-API", name="Delete API", price=Decimal("1.00"), is_active=True)
        resp = self.api.delete(f"/api/products/{p.pk}/")
        self.assertIn(resp.status_code, (204, 200))
        self.assertFalse(Product.objects.filter(pk=p.pk).exists())


class ProductsDeleteProtectionTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Acme")
        self.product = Product.objects.create(sku="SKU-1", name="Widget", price=Decimal("10.00"), is_active=True)
        self.order = Order.objects.create(customer=self.customer)
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            unit_price=Decimal("10.00"),
        )

    def test_product_delete_is_protected_when_used_in_orders(self):
        with self.assertRaises(ProtectedError):
            self.product.delete()
