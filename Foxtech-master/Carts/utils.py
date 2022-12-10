from .models import Cart

def get_or_create_cart(request):
    # Se almacena el usuario solo si esta autenticado
    user = request.user if request.user.is_authenticated else None

    # Se obtiene el identificador unico del carrito de compras almacenado en la sesion
    identifier = request.session.get('cart_id')

    # Se intenta obtener el carrito de compras con el identificador unico
    cart = Cart.objects.filter(identifier = identifier).first()

    # Si el carrito no existe, se procede a crear uno nuevo
    if cart is None:
        cart = Cart.objects.create(user = user)

    # Si el usuario esta autenticado y el carrito no tiene un usuario asignado, se procede a almacenar el usuario con el carrito ya creado
    if user and cart.user is None:
        cart.user = user
        cart.save()

    # Se actualiza el identificador unico del carrito de compras
    request.session['cart_id'] = cart.identifier

    return cart
def destroy_session_cart(request):
    request.session['cart_id'] = None