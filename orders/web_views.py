from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, DetailView

from .models import Order
from .forms import OrderForm, OrderItemFormSet


class OrderListView(ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 25
    ordering = ["-id"]


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/order_form.html"

    def get_success_url(self):
        return reverse("orders:detail", kwargs={"pk": self.object.pk})


class OrderDetailView(DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if "formset" not in ctx:
            ctx["formset"] = OrderItemFormSet(instance=self.object)
        return ctx

    def post(self, request, *args, **kwargs):
        """
        Handle add/edit/delete of line items directly on the detail page.
        """
        self.object = self.get_object()
        formset = OrderItemFormSet(request.POST, instance=self.object)

        if formset.is_valid():
            formset.save()
            messages.success(request, "Order items saved.")
            return redirect("orders:detail", pk=self.object.pk)

        # If invalid, re-render page with errors
        return render(
            request,
            "orders/order_detail.html",
            {"order": self.object, "formset": formset},
        )


class OrderDeleteView(DeleteView):
    model = Order
    template_name = "orders/order_confirm_delete.html"
    success_url = reverse_lazy("orders:list")
