from django.http import request
from django.views.generic import (
    ListView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order


class OrderListView(LoginRequiredMixin, ListView): 
    template_name = 'orders/orders_list.html'
    paginate_by = 15
    context_object_name = 'orders'

    def get_queryset(self, *args, **kwargs):
        queryset = self.request.user.orders.all()
        return queryset
