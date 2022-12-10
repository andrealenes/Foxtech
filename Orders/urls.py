from django.urls import path
from . import views

app_name = 'Orders'

urlpatterns = [
    path('', views.order_view, name = 'order'),
    path('address/', views.address_view, name = 'address'),
    path('payment/', views.payment_view, name = 'payment'),
    path('confirm/', views.confirm_order_view, name = 'confirm'),
    path('add-address/', views.add_another_address, name = 'add-address'),
    path('cancel-order/', views.cancel_order_view, name = 'cancel-order'),
    path('complete-order/', views.completed_order, name = 'complete-order'),
    path('download-bill/<str:number>', views.download_bill, name = 'download-bill'),
]