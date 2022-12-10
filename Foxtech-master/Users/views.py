from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth import login 
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.contrib.auth.decorators import login_required
from Users.models import UserModel
from django.contrib import messages
from Users.forms import RegisterForm
from Users.forms import ContactForm
from Users.forms import UpdateDataUserForm
from Users.forms import LoginForm
from django.conf import settings
import threading 
from .forms import ChangePassword
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_GET
from django.http import HttpResponseRedirect
from Orders.models import Address
from .forms import AddressForm
from .models import City
from Orders.common import OrderStatus
from Orders.models import AccountingDocument
from Orders.models import Order
from Products.models import Product
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic import DetailView

@require_http_methods(['GET', 'POST'])
def login_view(request):
    """
    Vista encargada de el inicio de sesion.
    """

    if request.user.is_authenticated:
        return redirect('index')

    if request.GET.get('next'):
        messages.error(request, 'Error debe iniciar sesion primero')

    formulario = LoginForm(request.POST or None)
    
    if request.method == 'POST' and formulario.is_valid():
        user = formulario.authenticate_user()

        if UserModel.objects.filter(email = request.POST.get('correo')).first() is None:
            messages.error(request, 'Usuario no registrado en el sistema')
        elif not UserModel.objects.filter(email = request.POST.get('correo')).first().is_active and UserModel.objects.filter(email = request.POST.get('correo')).first() != None:
                messages.error(request, 'Usuario inactivo, comuniquese con el administrador del sistema')
        elif user:
            login(request, user)

            if request.GET.get('next'):
                return HttpResponseRedirect(request.GET.get('next'))
            elif user.is_staff:
                return HttpResponseRedirect('/admin/')
            else:
                return redirect('index')
        else:
            messages.error(request, "Correo o contraseña incorrectos")
            
    return render(request, 'users/login.html', context = {'formulario': formulario})

@require_GET
@login_required
def logout_view(request):
    """
    Vista encargada de el cierre de sesion.
    """

    logout(request)
    messages.success(request, 'Sesion cerrada exitosamente')
    return redirect('Users:login')

@require_http_methods(['GET', 'POST'])
def register(request):
    """
    Vista encargada de el registro de usuarios.
    """

    if request.user.is_authenticated:
        return redirect('index')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()

        if user:
            thread = threading.Thread(target = form.send(request))

            thread.start()

            login(request, user)

            return redirect('index')

    return render(request, 'users/register.html', context={
        'formulario': form,
    })

@require_http_methods(['GET', 'POST'])
@login_required
def updateDataUser(request):
    """
    Vista encargada de renderizar el formulario para actualizar los datos, tratar los datos ingresados por el usuario y persistir los cambios en la base de datos.
    """

    # Datos adicionales del usuario almacenados en el UserModel
    usuario = UserModel.objects.get(email = request.user.email)

    # Enviar los datos del usuario al formulario.
    formulario = UpdateDataUserForm({
        'nombre': usuario.first_name,
        'apellido': usuario.last_name,
        'tipo_documento': usuario.type_of_document,
        'numero_documento': usuario.number_document,
        'ciudad': usuario.city,
        'direccion': usuario.main_address,
        'barrio': usuario.neighborhood,
        'correo': usuario.email,
        'telefono': usuario.phone_number,
        'genero': usuario.gender
    })

    if request.method == 'POST':
        formulario = UpdateDataUserForm(request.POST or None)
        email = request.POST.get('correo')

        if UserModel.objects.filter(email = email).exists() and email != request.user.email:
            messages.error(request, "Error el correo ya se encuentra registrado en el sistema")
        else:
            if formulario.is_valid():
                formulario.save(request.user)
                messages.success(request, "Informacion actualizada exitosamente")

    return render(request, 'users/dashboard_usuario/actualizarDatosUsuario.html', context={
        'formulario': formulario,
    })

class DashboardUserView(LoginRequiredMixin, TemplateView):
    """
    Vista para renderizar el template del dashboard del cliente.
    """

    template_name = 'users/dashboard_usuario/dashboardUsuario.html'

@require_http_methods(['GET', 'POST'])
def contact(request):
    """
    Vista todo el funcionamiento del formulario de contacto del aplicativo.
    """

    formulario = ContactForm(request.POST or None)

    if request.method == 'POST' and formulario.is_valid():
        formulario.send(request)
        messages.success(request, 'Enviado con exito, en 24h un asesor se contactara contigo')
        return redirect('Users:contact')

    return render(request, 'users/contacto.html', context={
        'formulario': formulario,
    })

@require_http_methods(['GET', 'POST'])
@login_required
def changePassword(request):
    """
    Vista para que un usuario loggeado pueda cambiar su contraseña desde el dashboard.
    """
    formulario = ChangePassword(request.POST or None)

    if request.method == 'POST' and formulario.is_valid():
        usuario = UserModel.objects.get(email = request.user.email)
        usuario.set_password(request.POST.get('contrasena'))
        usuario.save()

        messages.success(request, 'La contraseña se ha cambiado con exito.')
        return redirect('Users:login')

    return render(request, 'users/dashboard_usuario/cambiarContrasena.html', context = {
        'formulario': formulario,
    })

class AddressListView(LoginRequiredMixin, ListView):
    """
    Vista para ver todas las direcciones de un usuario para el envio de los pedidos.
    """

    template_name = 'users/dashboard_usuario/direcciones.html'
    model = Address
    context_object_name = 'direcciones'

    def get_queryset(self, *args, **kwargs):
        queryset = Address.objects.filter(user = self.request.user).order_by('-default')

        return queryset

@require_http_methods(['GET', 'POST'])
@login_required
def create_address_view(request):
    """
    Vista para que un usuario agregue una nueva direccion para el envio de los pedidos.
    """

    form = AddressForm(request.POST or None)
    antigua_direccion_principal = Address.objects.get(default = True, user = request.user)

    if request.method == 'POST' and form.is_valid():
        if Address.objects.filter(address = form.cleaned_data.get('direccion').strip(), user = request.user).exists():
            messages.error(request, 'Error la direccion ya esta registrada')
        else:
            if form.cleaned_data.get('defecto') == '2':
                antigua_direccion_principal.default = False
                antigua_direccion_principal.save()
            
            try:
                direccion = Address.objects.create(
                    user = request.user,
                    city = City.objects.get(description = form.cleaned_data.get('ciudad')),
                    address = form.cleaned_data.get('direccion').strip(),
                    default = True if form.cleaned_data.get('defecto') == '2' else False,
                    neighborhood = form.cleaned_data.get('barrio').strip()
                )

                if direccion.default:
                    user_information = UserModel.objects.get(user = request.user)
                    user_information.address = form.cleaned_data.get('direccion').strip()
                    user_information.neighborhood = form.cleaned_data.get('barrio').strip()
                    user_information.city = City.objects.get(description = form.cleaned_data.get('ciudad'))
                    user_information.save()

                messages.success(request, 'Nueva direccion agregada con exito')
                return redirect('Users:addresses')
            except:
                messages.error(request, 'Error la direccion no se pudo agregar')

    return render(request, 'users/dashboard_usuario/nueva_direccion.html', context = {
        'formulario': form,
    })

@require_GET
@login_required
def delete_address(request, id_address):
    """
    Vista para eliminar una direccion registrada por el usuario para el envio de los pedidos.
    """

    direccion = Address.objects.get(pk = id_address, user = request.user)

    if direccion.delete():
        messages.success(request, 'Direccion eliminada con exito')
    else:
        messages.error(request, 'Error no se pudo eliminar la direccion')

    return redirect('Users:addresses')

@require_http_methods(['GET', 'POST'])
@login_required
def edit_address(request, id_address):
    """
    Vista para editar las direcciones registradas por el usuario para el envio de los pedidos.
    """

    # Obtener la direccion que se desea editar de la base de datos
    direccion_actual = Address.objects.get(pk = id_address, user = request.user)

    # Crear una instancia del formulario con los datos de direccion a editar
    form = AddressForm({
        'ciudad': direccion_actual.city,
        'direccion': direccion_actual.address,
        'barrio': direccion_actual.neighborhood,
        'defecto': '2' if direccion_actual.default else '3'
    })    

    if request.method == 'POST':
        form = AddressForm(request.POST or None)
        # Nueva direccion agredada por el usuario
        direccion_formulario = request.POST.get('direccion').strip()

        # Verificar si la nueva direccion ya existe
        nueva_direccion = Address.objects.filter(address = direccion_formulario, user = request.user)

        if form.is_valid():
            if nueva_direccion.exists() and direccion_formulario != direccion_actual.address:
                messages.error(request, 'Error la direccion ya esta registrada')
            elif direccion_actual.default and form.cleaned_data.get('defecto') == '3':
                messages.error(request, 'No se pudo actualizar porque debe tener una direccion por defecto')
            else:
                if form.cleaned_data.get('defecto') == '2':
                    direccion_por_defecto = Address.objects.get(default = True, user = request.user)
                    direccion_por_defecto.default = False
                    direccion_por_defecto.save()

                resultado = form.save(direccion_actual.id_address, request.user)
                if resultado.default:  
                    user_information = UserModel.objects.get(email = request.user.email)
                    user_information.address = form.cleaned_data.get('direccion').strip()
                    user_information.neighborhood = form.cleaned_data.get('barrio').strip()
                    user_information.city = City.objects.get(description = form.cleaned_data.get('ciudad'))
                    user_information.save()
                
                messages.success(request, 'Direccion actualizada con exito')
                return redirect('Users:addresses')

    return render(request, 'users/dashboard_usuario/editar_direccion.html', context = {
        'formulario': form,
    })

@login_required
def config_account_view(request):
    return render(request, 'users/dashboard_usuario/configuracion_cuenta.html', context = {})

class OrdersListView(LoginRequiredMixin, ListView):
    """
    Vista para ver listar todos los pedidos realizados por el usuario.
    """

    template_name = 'users/dashboard_usuario/pedidosUsuario.html'
    model = UserModel
    context_object_name = 'pedidos'

    def get_queryset(self, *args, **kwargs):
        queryset = UserModel.objects.get(email = self.request.user.email).get_orders_completed_and_canceled()

        return queryset

@login_required
def purchases_view(request):
    orders_payed = UserModel.objects.get(email = request.user.email).get_orders_payed().order_by('-id_order')
    purchases = [AccountingDocument.objects.get(order = item) for item in orders_payed]

    return render(request, 'users/dashboard_usuario/comprasUsuario.html', context = {
        'compras': purchases,
    })

class DetailOrderView(LoginRequiredMixin, DetailView):
    """
    Vista para ver el detalle de un pedido del usuario.
    """

    template_name = 'users/dashboard_usuario/detallePedido.html'
    model = Order
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orden'] = context['object']
        return context

class DetailPurchaseView(LoginRequiredMixin, DetailView):
    """
    Vista para ver el detalle de una compra del usuario.
    """
    
    template_name = 'users/dashboard_usuario/detalleCompra.html'
    model = AccountingDocument
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['compra'] = context['object']
        return context

@login_required
def cancel_order(request, identifier):
    """
    Vista encargada de realizar la cancelacion de la orden.
    """

    order = Order.objects.get(identifier = identifier)

    if request.user.id_user != order.user.id_user:
        return redirect('index')

    # Devolver los productos al stock
    for item in order.cart.cartproducts_set.all():
        product = Product.objects.get(pk = item.product.id_product)
        product.outputs -= item.quantity
        product.save()

    order.cancel()

    messages.success(request, 'Orden de compra cancelada con exito')

    return redirect('Users:orders')