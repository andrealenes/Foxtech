from Products.models import Category
from django.shortcuts import render
from Products.models import Product
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .utils import random_products
from .utils import order_products_in_category
from .utils import order_search_products
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404

class ProductDetailView(DetailView):
    """
    Vista encargada del detalle del pedido.
    """
    
    model = Product
    template_name = 'products/producto.html'

    def get_queryset(self):
        return Product.objects.filter(state = True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['producto'] = context['object']
        context['productos_aleatorios'] = random_products(context['object'])
        return context

@require_GET
def category_detail(request, slug):
    """
    Vista encargada del detalle de la categoria.
    """
    
    categoria = get_object_or_404(Category, slug = slug)
    productos = categoria.products.all()
    parametro_busqueda = ''
    cantidad_productos = 0

    # Buscar y ordenar el resultado de los productos.
    if request.GET.get('ordenar') and request.GET.get('q'):
        parametro_busqueda = request.GET.get('q')
        productos = categoria.products.filter(Q(name__icontains = parametro_busqueda) | Q(description__icontains = parametro_busqueda), state = True)
        productos = order_search_products(productos, request.GET.get('ordenar'))
        cantidad_productos = productos.count()

    # Solo ordenar los productos
    elif request.GET.get('ordenar'):
        parametro_orden = request.GET.get('ordenar')
        productos = order_products_in_category(categoria, parametro_orden)

    # Buscar un producto que pertenezca a esa categoria.
    elif request.GET.get('q'):
        parametro_busqueda = request.GET.get('q')
        productos = categoria.products.filter(Q(name__icontains = parametro_busqueda) | Q(description__icontains = parametro_busqueda), state = True)
        cantidad_productos = productos.count()

    # Paginacion
    paginacion = Paginator(productos, 10)
    num_pagina = request.GET.get('page', 1)
    productos = paginacion.get_page(num_pagina)

    return render(request, 'products/categoria.html', context = {
        'categoria': categoria,
        'productos': productos,
        'paginacion': paginacion,
        'cantidad_productos': cantidad_productos,
        'parametro_busqueda': parametro_busqueda,
    })

@require_GET
def search_in_all_product(request):
    """
    Vista encargada de la busqueda de productos.
    """

    contexto = {}
    if request.GET.get('q') or request.GET.get('ordenar'):
        busqueda = request.GET.get('q')
        productos = Product.objects.filter(Q(name__icontains = busqueda) | Q(description__icontains = busqueda))
        cantidad = productos.count

        if request.GET.get('ordenar'):
            productos = order_search_products(productos, request.GET.get('ordenar'))

        # Paginacion
        paginacion = Paginator(productos, 7)
        num_pagina = request.GET.get('page', 1)
        productos = paginacion.get_page(num_pagina)

        contexto = {
            'productos': productos,
            'paginacion': paginacion,
            'busqueda': request.GET.get('q'),
            'cantidad_productos': cantidad
        }

    
    return render(request, 'products/busqueda producto.html', contexto)