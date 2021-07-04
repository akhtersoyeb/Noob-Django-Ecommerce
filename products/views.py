from django.views.generic import (
    View,
    ListView,
    DetailView,
    TemplateView
)
from .models import Product, Category
from orders.models import Order
from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib import messages

import razorpay
key_id = settings.RAZORPAY_KEY_ID
key_secret = settings.RAZORPAY_KEY_SECRET
client = razorpay.Client(auth=(key_id, key_secret))


class CategoryProductsListView(ListView):
    template_name = 'products/products_list.html'
    paginate_by = 15
    context_object_name = 'products'

    def get_queryset(self, *args, **kwargs):
        slug = self.kwargs['slug']
        category = Category.objects.get(slug=slug)
        # queryset = category.products.filter(available=True)
        queryset = Product.objects.filter(category=category)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryProductsListView,
                        self).get_context_data(*args, **kwargs)
        slug = self.kwargs['slug']
        category = Category.objects.get(slug=slug)
        context['category'] = category
        return context


class ProductDetailsView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'


@method_decorator(csrf_exempt, name='dispatch')
class ProductPurchaseView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        product = Product.objects.get(slug=self.kwargs["slug"])
        order_amount = int(product.price * 100)
        order_currency = 'INR'
        order = client.order.create(
            dict(amount=order_amount, currency=order_currency))
        context = {
            'order_id': order['id'],
            'amount': order['amount'],
            'key_id': key_id
        }
        return JsonResponse(context, safe=False)

    def post(self, request, *args, **kwargs):
        product = Product.objects.get(slug=self.kwargs["slug"])
        razorpay_order_id = request.POST['razorpay_order_id']
        razorpay_payment_id = request.POST['razorpay_payment_id']
        razorpay_signature = request.POST['razorpay_signature']
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            check_signature = client.utility.verify_payment_signature(params_dict)
            new_order = product.orders.create(
                owner = request.user,
                status='initiated',
                order_id=str(razorpay_order_id),
                payment_id=str(razorpay_payment_id),
                signature=str(razorpay_signature)
            )
            messages.add_message(request, messages.SUCCESS, 'You order is successful. Delivery expected on 34/32/32')
        except:
            messages.add_message(request, messages.SUCCESS,'Error occurred. Try again later.')

        return redirect('products:product_detail', slug=product.slug)
