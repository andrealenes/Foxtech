from django.shortcuts import render
from .models import Cart
from .utils import get_or_create_cart
from Products.models import Product
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_GET
from .models import CartProducts
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

class CartView(TemplateView):
    """
    Vista para ver el detalle(productos, total, subtotal, cantidad) del carrito de compras.
    """
    template_name = 'cart/carrito de compras.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carrito'] = get_or_create_cart(self.request)
        return context

@require_POST
def add_product(request):
    """
    Vista para agregar un producto al carrito de compras.
    """
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, pk = request.POST.get('product_id'))
    quantity = int(request.POST.get('quantity', 1))

    cart_product = CartProducts.objects.create_or_update_quantity(cart, product, quantity)

    if quantity == 1:
        messages.success(request, 'Producto agregado al carrito exitosamente.')
    else:
        messages.success(request, 'Productos agregados al carrito exitosamente.')

    url_peticion = request.POST.get('url')

    return HttpResponseRedirect(url_peticion)

@require_POST
def remove_product(request):
    """
    Vista para eliminar un producto del carrito de compras.
    """
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, pk = request.POST.get('product_id'))

    cart.product.remove(product)
    messages.success(request, 'Producto eliminado del carrito.')

    return redirect('Carts:cart')

@require_GET
def clear_cart(request):
    """
    Vista encargada de vaciar el carrito de compras.
    """
    # Se obtiene el carrito de compras
    cart = get_or_create_cart(request)

    # Mediante cartproducts_set se accede a los datos de la tabla intermedia que se creo en la relacion muchos a muchos entre Cart y Product, luego usando los metodos all() y delete() eliminamos todos los productos que estan relacionados con el carrito.
    cart.cartproducts_set.all().delete()
    cart.update_totals()
    cart.save()

    messages.success(request, 'Carrito vaciado exitosamente.')
    return redirect('Carts:cart')

@require_POST
def modify_quantity(request):
    """
    Vista encargada de modificar la cantidad de un producto del carrito de compras.
    """
    # Se obtiene el carrito de compras
    cart = get_or_create_cart(request)

    # Se captura la accion a realizar (agregar o disminuir cantidad)
    action = request.POST.get('action')

    # Se captura el producto que se le va a modificar la cantidad
    product = request.POST.get('product_id')
    cart = cart.cartproducts_set.get(product = product)

    if action == 'aumentar-cantidad':
        cart.quantity += 1
        cart.save()
    else:
        cart.quantity -= 1
        cart.save()

    return redirect('Carts:cart')

@require_GET
@login_required
def check_quantity_cart(request):
    """
    Vista encargada de comprobar que la cantidad de productos en el carrito de compras tengan el stock suficiente.
    """
    cart = get_or_create_cart(request)
    descontar_stock = False

    # Recorrer los productos agregados en el carrito para contrastar con el stock disponible, si la cantidad pedida por el usuario es mayor a lo que se tiene en stock entonces se procede disminuir la cantidad 
    for item in cart.cartproducts_set.all():
        producto = Product.objects.get(pk = item.product_id)
        if item.quantity > producto.stock:
            # Si el stock del producto es igual a cero, entonces se elimina el producto del carrito.
            if producto.stock == 0:
                cart.product.remove(producto)
            else:
                item.quantity = producto.stock
                item.save()

            descontar_stock = True

    if descontar_stock:
        messages.info(request, 'Algunos productos no cuentan con el suficiente stock, se ajustaron los productos al stock disponible en el momento')
        return redirect('Carts:cart')

    return redirect('Orders:order')