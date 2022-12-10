from .models import Cart

def get_quantity_products_cart(request):
    """Funcion para obtener la cantidad de productos que el usuario agrego al carrito"""

    # Se obtiene el carrito
    cart = Cart.objects.filter(identifier = request.session.get('cart_id')).first()

    # Se define la variable que almacenara la cantidad de productos
    cantidad_productos_carrito = 0

    # Se comprueba si existe el carrito y si el carrito tiene asociado productos
    if cart and cart.product.exists():
        cantidad_productos_carrito = cart.product.count()

    return {'cantidad_productos_carrito': cantidad_productos_carrito}