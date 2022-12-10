from .models import Order
from django.urls import reverse

def get_or_create_order(request, cart):
    """
    Funcion de ayuda para obtener o crear una instancia de la orden y almacenarlo en la session.
    """

    order = cart.order

    if order is None and request.user.is_authenticated:
        order = Order.objects.create(cart = cart, user = request.user)

    if order:
        request.session['order_id'] = order.identifier

    return order

def breadcrumb(products = True, address = False, payment = False, confirm = False):
    return [
        {'title': 'Productos', 'active': products, 'url': reverse('Orders:order')},
        {'title': 'Dirección', 'active': address, 'url': reverse('Orders:address')},
        {'title': 'Pago', 'active': payment, 'url': reverse('Orders:payment')},
        {'title': 'Confirmación', 'active': confirm, 'url': reverse('Orders:confirm')},
    ]

def destroy_session_order(request):
    """
    Funcion de ayuda para eliminar la orden de la sesion.
    """
    
    request.session['order_id'] = None