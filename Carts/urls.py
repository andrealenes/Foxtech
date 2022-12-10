from django.urls import path
from . import views

app_name = 'Carts'

urlpatterns = [
    path('', views.CartView.as_view(), name = 'cart'),
    path('add-product/', views.add_product, name = 'add_product'),
    path('remove-product/', views.remove_product, name = 'remove_product'),
    path('clear-cart/', views.clear_cart, name = 'clear_cart'),
    path('modify-quantity/', views.modify_quantity, name = 'modify_quantity_product'),
    path('check-quantity/', views.check_quantity_cart, name = 'check_quantity_cart'),
]