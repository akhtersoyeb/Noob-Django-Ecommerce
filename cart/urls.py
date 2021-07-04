from django.urls import path 

from . import views 

app_name = 'cart'

urlpatterns = [ 
    path('', views.CartView.as_view(), name='cart'),
    path('<slug:slug>/add/', views.AddToCartView.as_view(), name='add'),
    path('<slug:slug>/remove/', views.RemoveFromCartView.as_view(), name='remove'),
    path('purchase/', views.CartPurchaseView.as_view(), name='purchase'), 
    
    
]