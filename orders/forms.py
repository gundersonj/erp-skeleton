from django import forms
from django.forms import inlineformset_factory
from decimal import Decimal

from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer", "status"]


class OrderItemForm(forms.ModelForm):
    unit_price = forms.DecimalField(max_digits=12, decimal_places=2, required=False)

    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "unit_price"]

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        unit_price = cleaned.get("unit_price")

        # If user leaves unit_price blank, default from product.price
        if product and (unit_price is None):
            cleaned["unit_price"] = product.price

        return cleaned


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)
