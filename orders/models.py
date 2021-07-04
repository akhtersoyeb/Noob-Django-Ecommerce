from django.db import models
from products.models import Product
from django.contrib.auth.models import User 

class Order(models.Model):

    STATUS_CHOICES = (
        ('initiated', 'Initiated'),
        ('packed', 'Packed'),
        ('delivered', 'Deliverd')
    )
    owner = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    product = models.ManyToManyField(
        Product, 
        related_name='orders',
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='initiated')
    order_id = models.CharField(max_length=200)
    payment_id = models.CharField(max_length=200)
    signature = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.username} | {self.date_created}"


