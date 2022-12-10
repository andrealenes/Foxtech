from .models import Product
import random

def random_products(product):
    productos = Product.objects.exclude(pk = product.id_product, stock = 0)
    cantidad_productos = abs(Product.objects.all().count() - 12)
    numero_aleatorio = random.randint(1, cantidad_productos)

    return productos[numero_aleatorio:numero_aleatorio + 12]

def order_products_in_category(categoria, parametro_orden):
    """
    Esta funcion ordena los productos que pertenecen a una categoria especifica.
    """
    resultado = categoria.products.all()

    if parametro_orden == '1':
        resultado = categoria.products.all().order_by('final_price')
    elif parametro_orden == '2':
        resultado = categoria.products.all().order_by('-final_price')
    elif parametro_orden == '3':
        resultado = categoria.products.all().order_by('name')
    elif parametro_orden == '4':
        resultado = categoria.products.all().order_by('-name')
    elif parametro_orden == '5':
        resultado = categoria.products.exclude(discount = 0).order_by('-discount')

    return resultado

def order_search_products(productos, parametro_orden):
    """
    Esta funcion ordena todos los productos, dependiendo el parametro que reciba.
    """
    resultado = productos

    if parametro_orden == '1':
        resultado = productos.order_by('final_price')
    elif parametro_orden == '2':
        resultado = productos.order_by('-final_price')
    elif parametro_orden == '3':
        resultado = productos.order_by('name')
    elif parametro_orden == '4':
        resultado = productos.order_by('-name')
    elif parametro_orden == '5':
        resultado = productos.exclude(discount = 0).order_by('-discount')

    return resultado