from django.shortcuts import render, redirect
from django.views.generic import (
    View, 
    TemplateView, 
    DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.conf import settings

from .models import Cart 
from products.models import Product
from orders.models import Order


import razorpay
key_id = settings.RAZORPAY_KEY_ID
key_secret = settings.RAZORPAY_KEY_SECRET
client = razorpay.Client(auth=(key_id, key_secret))

class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'cart/cart.html'
    context_object_name = 'cart' 

    def get_context_data(self, *args, **kwargs):
        context = super(CartView,
                        self).get_context_data(*args, **kwargs)
        total_price = 0 

        # Check if user has a cart object or not
        if hasattr(self.request.user, 'cart'):
            cart = self.request.user.cart 
        else : 
            cart = Cart(owner=self.request.user)
            cart.save() 
        
        for product in cart.products.all() :
            total_price += product.price 
        context['cart'] = cart 
        context['total_price'] = total_price
        return context


class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs): 
        product = Product.objects.get(slug=self.kwargs["slug"])

        # Check if user has a cart object or not
        if hasattr(self.request.user, 'cart') : 
            cart = self.request.user.cart 
        else : 
            cart = Cart(owner=self.request.user)
            cart.save() 

        # Check if product is in the cart already
        if product in cart.products.all() : 
            messages.add_message(request, messages.SUCCESS, 'Product is already in the cart.')
            return redirect('products:product_detail', slug=product.slug)

        cart.products.add(product)
        cart.save() 
        messages.add_message(
            request, messages.SUCCESS, 'Product successfully added to cart.'
        )
        return redirect('products:product_detail', slug=product.slug)


class RemoveFromCartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs): 

        # Check if user has a cart object or not
        if hasattr(self.request.user, 'cart') : 
            cart = self.request.user.cart 
        else : 
            cart = Cart(owner=self.request.user)
            cart.save() 
        
        product = Product.objects.get(slug=self.kwargs["slug"])

        # Check if product is in the cart 
        if product in cart.products.all(): 
            cart.products.remove(product)
            cart.save() 
            messages.add_message(request, messages.SUCCESS, 'Product removed from the cart.')
            return redirect('cart:cart')
        else : 
            messages.add_message(request, messages.SUCCESS, 'Product not found in the cart.')
            return redirect('cart:cart')


@method_decorator(csrf_exempt, name='dispatch')
class CartPurchaseView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        # Check if user has a cart or not
        if hasattr(self.request.user, 'cart') : 
            cart = self.request.user.cart 
        else : 
            messages.add_message(request, messages.SUCCESS, 'You dont have any products in the cart to buy!')
            return redirect('cart:cart')
        
        # Check if cart has atleast one product 
        if cart.products.all().count == 0 :
            messages.add_message(request, messages.SUCCESS, 'You dont have any products in the cart to buy!')
            return redirect('cart:cart')
        
        order_amount = 0
        for product in cart.products.all() :
            order_amount += product.price
        order_amount = int(order_amount * 100)
        order_currency = 'INR'
        order = client.order.create(dict(amount=order_amount, currency=order_currency))
        context = {
            'order_id': order['id'],
            'amount': order['amount'],
            'key_id': key_id
        }
        return JsonResponse(context, safe=False)

    def post(self, request, *args, **kwargs):
        cart = self.request.user.cart 
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
            new_order = Order(
                owner = request.user, 
                status = 'initiated', 
                order_id = str(razorpay_order_id),
                payment_id=str(razorpay_payment_id),
                signature=str(razorpay_signature)
            )
            new_order.save() 
            for product in cart.products.all() :
                new_order.product.add(product)
            new_order.save() 
            messages.add_message(request, messages.SUCCESS, 'You order is successful. Delivery expected on 34/32/32')
        except:
            messages.add_message(request, messages.SUCCESS,'Error occurred. Try again later.')

        return redirect('order:list')
