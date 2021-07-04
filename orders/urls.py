from django.urls import path 
from . import views 

app_name = 'order'

urlpatterns = [ 
    path('my-orders/', views.OrderListView.as_view(), name='list')
]