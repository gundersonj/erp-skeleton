from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError

from orders.models import Order
from customers.models import Customer


class CustomersWebViewTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Acme",
            email="acme@example.com",
            phone="555-111-2222",
            notes="Test notes",
        )

    def test_customers_list_page_loads(self):
        resp = self.client.get(reverse("customers:list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Customers")
        self.assertContains(resp, "Acme")

    def test_create_customer(self):
        resp = self.client.post(
            reverse("customers:create"),
            data={
                "name": "Globex",
                "email": "globex@example.com",
                "phone": "555-333-4444",
                "notes": "New customer",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Customer.objects.filter(name="Globex").exists())

    def test_update_customer(self):
        resp = self.client.post(
            reverse("customers:update", kwargs={"pk": self.customer.pk}),
            data={
                "name": "Acme Updated",
                "email": self.customer.email,
                "phone": self.customer.phone,
                "notes": self.customer.notes,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, "Acme Updated")

    def test_delete_customer(self):
        c = Customer.objects.create(name="Delete Me")
        resp = self.client.post(reverse("customers:delete", kwargs={"pk": c.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Customer.objects.filter(pk=c.pk).exists())


class CustomersApiTests(TestCase):
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

        self.customer = Customer.objects.create(
            name="Acme",
            email="acme@example.com",
            phone="555-111-2222",
            notes="Test notes",
        )

    def test_list_customers(self):
        resp = self.api.get("/api/customers/")
        self.assertEqual(resp.status_code, 200)
        # DRF returns list (or paginated dict). Handle both.
        data = resp.data["results"] if isinstance(resp.data, dict) and "results" in resp.data else resp.data
        self.assertGreaterEqual(len(data), 1)

    def test_create_customer_via_api(self):
        resp = self.api.post(
            "/api/customers/",
            {"name": "Globex", "email": "globex@example.com", "phone": "555-333-4444", "notes": ""},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Customer.objects.filter(name="Globex").exists())

    def test_update_customer_via_api(self):
        resp = self.api.patch(
            f"/api/customers/{self.customer.pk}/",
            {"name": "Acme API Updated"},
            format="json",
        )
        self.assertIn(resp.status_code, (200, 202))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, "Acme API Updated")

    def test_delete_customer_via_api(self):
        c = Customer.objects.create(name="Delete API")
        resp = self.api.delete(f"/api/customers/{c.pk}/")
        self.assertIn(resp.status_code, (204, 200))
        self.assertFalse(Customer.objects.filter(pk=c.pk).exists())


class CustomersDeleteProtectionTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Acme")
        self.order = Order.objects.create(customer=self.customer)

    def test_customer_delete_is_protected_when_has_orders(self):
        with self.assertRaises(ProtectedError):
            self.customer.delete()
