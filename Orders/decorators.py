from .utils import get_or_create_order
from Carts.utils import get_or_create_cart

def get_cart_and_order(function):
    def wrap(request, *args, **kwargs):
        cart = get_or_create_cart(request)
        order = get_or_create_order(request, cart)

        return function(request, cart, order, *args, **kwargs)
    
    return wrap