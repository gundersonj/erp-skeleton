from django import forms
from django.forms import inlineformset_factory

from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer", "status"]


class OrderItemForm(forms.ModelForm):
    # Let user omit unit_price; we’ll default from Product.price
    unit_price = forms.DecimalField(max_digits=12, decimal_places=2, required=False)

    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "unit_price"]

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        unit_price = cleaned.get("unit_price")

        if product and unit_price in (None, ""):
            cleaned["unit_price"] = product.price

        return cleaned


OrderItemFormSet = inlineformset_factory(
    parent_model=Order,
    model=OrderItem,
    form=OrderItemForm,
    extra=1,          # show 1 blank line item row
    can_delete=True,  # allow removing items
)
