from django.urls import path 
from . import views 

app_name = 'products'

urlpatterns = [ 
    path('<slug:slug>/list/', views.CategoryProductsListView.as_view(), name='products_list'),
    path('<slug:slug>/details/', views.ProductDetailsView.as_view(), name='product_detail'),
    path('<slug:slug>/purchase/', views.ProductPurchaseView.as_view(), name='purchase'),

]