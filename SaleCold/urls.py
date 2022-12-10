from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name = 'index'),
    path('info/', views.InfoTemplateView.as_view(), name = 'info'),
    path('users/', include('Users.urls')),
    path('products/', include('Products.urls')),
    path('reset_password/', views.reset_password, name ='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='users/restablecer_contraseña/envio_mail_recuperar_contraseña.html'), name ='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name = 'users/restablecer_contraseña/formulario_recuperar_contraseña.html'), name ='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name = 'users/restablecer_contraseña/confirmacion_recuperacion_contraseña.html'), name ='password_reset_complete'),
    path('cart/', include('Carts.urls')),
    path('order/', include('Orders.urls')),
] 

# Agregar la ruta y el directorio donde se almacenara la media de la aplicacion al urlpatterns.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)