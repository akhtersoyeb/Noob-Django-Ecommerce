from django.db import models
from django.contrib.auth.models import User 
from products.models import Product

class Cart(models.Model):
    owner = models.OneToOneField(
        User, 
        related_name='cart',
        on_delete=models.CASCADE,
    )
    products = models.ManyToManyField(
        Product,
        related_name='cart', 
        null=True, 
        blank=True 
    )

    def __str__(self):
        return self.owner.username

# class Item(models.Model):
#     cart = models.ForeignKey(
#         Cart, 
#         related_name='items',
#         on_delete=models.CASCADE
#     )
#     product = models.ManyToManyField(
#         Product, 
#         related_name='cart', 
#     )
#     amount = models.PositiveBigIntegerField(default=1)
#     unit_price = models.DecimalField(max_digits=10, decimal_places=2)


