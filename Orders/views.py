from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .utils import breadcrumb
from .models import TypeOfDelivery
from .models import PaymentType
from .models import Address
from django.contrib import messages
from Users.forms import AddressForm
from Users.models import City
from Carts.utils import destroy_session_cart
from .utils import destroy_session_order
from Products.models import Product
from .decorators import get_cart_and_order
from SaleCold.utils import send_email
import threading 

# Configuracion para windows
#import os
#os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")


#from weasyprint import HTML
#from weasyprint.text.fonts import FontConfiguration
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from .common import OrderStatus
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import reverse
from .models import AccountingDocument
from Users.models import UserModel
from io import BytesIO
from xhtml2pdf import pisa  

@login_required
@get_cart_and_order
def order_view(request, cart, order):
    """
    Vista encargada del resumen del pedido.
    """

    if not cart.has_products():
        messages.error(request, 'Debes agregar primero productos al carrito de compras')
        return redirect('Carts:cart')

    return render(request, 'orders/pedido.html', context = {
        'carrito': cart,
        'orden': order,
        'breadcrumb': breadcrumb(),
    })

@login_required
@get_cart_and_order
def address_view(request, cart, order):
    """
    Vista encargada del metodo de envio del pedido.
    """

    if not cart.has_products():
        messages.error(request, 'Debes agregar primero productos al carrito de compras')
        return redirect('Carts:cart')
    elif request.method == 'POST' and request.POST.get('metodo_entrega'):
        if request.POST.get('metodo_entrega') == 'Entrega a domicilio':
            order.shipping_total = 8000
            order.address = Address.objects.get(user = request.user, address = request.POST.get('direccion'))
        else:
            order.shipping_total = 0
            order.address = None

        order.type_of_delivery = TypeOfDelivery.objects.get(description = request.POST.get('metodo_entrega'))
        order.save()
        return redirect('Orders:payment')

    types_of_delivery = TypeOfDelivery.objects.filter(state = True)
    addresses = Address.objects.filter(user = request.user)

    return render(request, 'orders/direccion.html', context = {
        'carrito': cart,
        'orden': order,
        'breadcrumb': breadcrumb(address=True),
        'tipos_de_envio': types_of_delivery,
        'direcciones': addresses,
    })

@login_required
@get_cart_and_order
def payment_view(request,cart, order):
    """
    Vista encargada del metodo de pago del pedido.
    """

    payment_methods = PaymentType.objects.filter(state = True)

    if request.method == 'POST' and request.POST.get('metodo_pago'):
        order.payment_type = PaymentType.objects.get(description = request.POST.get('metodo_pago'))
        order.save()
        return redirect('Orders:confirm')
    elif not cart.has_products():
        messages.error(request, 'Debes agregar primero productos al carrito de compras')
        return redirect('Carts:cart')
    elif order.type_of_delivery is None:
        messages.error(request, 'Debes seleccionar un metodo de entrega primero')
        return redirect('Orders:address')

    return render(request, 'orders/pago.html', context = {
        'carrito': cart,
        'orden': order,
        'breadcrumb': breadcrumb(address = True, payment = True),
        'metodos_de_pago': payment_methods,
    })

@login_required
@get_cart_and_order
def confirm_order_view(request, cart, order):
    """
    Vista para confirmar el pedido.
    """

    if order.type_of_delivery.description == 'Entrega a domicilio' and order.address == None:
        messages.error(request, 'Debes seleccionar una direccion de envio valida')
        return redirect('Orders:address')
    elif not cart.has_products():
        messages.error(request, 'Debes agregar primero productos al carrito de compras')
        return redirect('Carts:cart')
    elif order.type_of_delivery is None:
        messages.error(request, 'Debes seleccionar un metodo de entrega primero')
        return redirect('Orders:address')
    elif order.payment_type is None:
        messages.error(request, 'Debes seleccionar un metodo de pago primero')
        return redirect('Orders:payment')

    return render(request, 'orders/confirmacion.html', context = {
        'carrito': cart,
        'orden': order,
        'breadcrumb': breadcrumb(address = True, payment = True, confirm = True)
    })

@login_required
def add_another_address(request):
    """
    Vista para agregar otra direccion en el pedido.
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
                return redirect('Orders:address')
            except:
                messages.error(request, 'Error la direccion no se pudo agregar')

    return render(request, 'orders/agregar_direccion.html', context = {
        'formulario': form,
    })

@login_required
@get_cart_and_order
def cancel_order_view(request, cart, order):
    """
    Vista encargada de cancelar la orden.
    """

    if request.user.id != order.user_id:
        return redirect('Carts:cart')
        
    order.cancel()

    destroy_session_cart(request)
    destroy_session_order(request)
    messages.success(request, 'Orden de compra cancelada exitosamente')
    
    return redirect('index')

@login_required
@get_cart_and_order
def completed_order(request, cart, order):
    """
    Vista encargada de completar la orden.
    """

    if request.user.id_user != order.user_id:
        return redirect('Carts:cart')

    """
    1). Se descuenta el stock de los productos.
    2). Se genera el pedido.
    3). Se envia el correo confirmando el pedido.
    4). La orden queda en estado completado.
    5). Se espera el pago, si el pago es realizado, entonces se procede a enviar la factura al correo y se genera la instancia del documento contable.
    """

    template = 'mails/plantillaConfirmacionPedido.html'
    context = {
        'usuario': f"{order.user.first_name.split()[0]} {order.user.last_name.split()[0]}",
        'dominio': get_current_site(request).domain,
        'url': reverse('index'),
        'orden': order,
        'tipo_envio': order.type_of_delivery.description,
        'tipo_pago': order.payment_type.description,
    }

    send_email(template, context, f'🛒 Recibimos tu pedido {order.identifier}', order.user.email)

    # Descontar stock de los productos
    for item in cart.cartproducts_set.all():
        product = Product.objects.get(pk = item.product.id_product)
        product.outputs += item.quantity
        product.save()

    order.completed()

    destroy_session_cart(request)
    destroy_session_order(request)
    messages.success(request, 'Orden de compra completada exitosamente')

    return redirect('index')

def download_bill(request, number):
    """
    Vista encargada de generar la factura y descargarla.
    """

    accounting_document = AccountingDocument.objects.get(number_accounting_document = number)
    user_information = UserModel.objects.get(email = accounting_document.order.user.email)

    context = {
        'number_accounting_document': accounting_document.number_accounting_document,
        'nombre': f'{accounting_document.order.user.first_name.split()[0]} {accounting_document.order.user.last_name.split()[0]}',
        'tipo_documento': user_information.type_of_document,
        'numero_documento': user_information.number_document,
        'correo': accounting_document.order.user.email,
        'telefono': user_information.phone_number,
        'direccion': f'{user_information.main_address}, {user_information.city}',
        'fecha': accounting_document.accounting_document_date,
        'carrito': accounting_document.order.cart,
        'orden': accounting_document.order,
    }

    html = render_to_string("orders/factura.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; factura.pdf"
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
         return HttpResponse(result.getvalue(), content_type='application/pdf')

    """
    font_config = FontConfiguration()

    thread = threading.Thread(target = HTML(string=html).write_pdf(response, font_config=font_config))

    thread.start()"""

    return None