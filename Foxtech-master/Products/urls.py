from django.urls import path
from . import views

app_name = "Products"

urlpatterns = [
    path('search/', views.search_in_all_product, name='search'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product'),
    path('category/<slug:slug>/', views.category_detail, name='category'),
]