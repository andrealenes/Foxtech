from django.urls import path
from . import views

app_name = 'Users'

urlpatterns = [
    path('login/', views.login_view, name = "login"),
    path('logout/', views.logout_view, name = "logout"),
    path('account/', views.DashboardUserView.as_view(), name='dashboard-user'),
    path('update-data-user/', views.updateDataUser, name = "update-data-user"),
    path('contact/', views.contact, name = "contact"),
    path('register/', views.register, name = "register"),
    path('change-password/', views.changePassword, name = 'change-password'),
    path('addresses/', views.AddressListView.as_view(), name = 'addresses'),
    path('addresses/new/', views.create_address_view, name = 'new-address'),
    path('addresses/delete/<int:id_address>/', views.delete_address, name = 'delete-address'),
    path('addresses/edit/<int:id_address>/', views.edit_address, name = 'edit-address'),
    path('addresses/config/', views.config_account_view, name = 'config-account'),
    path('orders/', views.OrdersListView.as_view(), name = 'orders'),
    path('purchases/', views.purchases_view, name = 'purchases'),
    path('detail-order/<int:pk>', views.DetailOrderView.as_view(), name = 'detail-order'),
    path('detail-purchase/<int:pk>', views.DetailPurchaseView.as_view(), name = 'detail-purchase'),
    path('cancel-order/<str:identifier>', views.cancel_order, name = 'cancel-order'),
]