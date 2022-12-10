from django.db import models
from Users.models import UserModel
from Products.models import Product
from django.db.models.signals import pre_save
from django.db.models.signals import m2m_changed
from django.db.models.signals import post_save
from Orders.common import OrderStatus
import uuid

class Cart(models.Model):
    id_cart = models.AutoField('Id carrito', primary_key = True)
    user = models.ForeignKey(UserModel, verbose_name = 'Usuario', null = True, blank = True, on_delete = models.CASCADE)
    product = models.ManyToManyField(Product, through = 'Carts.CartProducts')
    total = models.PositiveIntegerField('Total', default = 0)
    subtotal = models.PositiveIntegerField('Subtotal', default = 0)
    create = models.DateTimeField('Fecha de creacion', auto_now_add = True)
    modified = models.DateTimeField('Fecha de modificacion', auto_now = True) 
    identifier = models.CharField('Identificador unico' , unique = True, max_length = 100)

    IVA = 0.19

    def __str__(self):
        return self.identifier

    def update_subtotal(self):
        self.subtotal = sum([ 
            object.product.final_price * object.quantity  for object in self.products_related() 
        ])

        self.save()

    def total_iva(self):
        return round(self.subtotal * self.IVA)

    def update_total(self):
        self.total = self.subtotal + (self.subtotal * Cart.IVA)
        self.save()

    def update_totals(self):
        self.update_subtotal()
        self.update_total()

        if self.order:
            self.order.update_total()

    def products_related(self):
        return self.cartproducts_set.select_related('product')
    
    @property
    def order(self):
        return self.order_set.filter(state = OrderStatus.CREATED.value).first()

    def has_products(self):
        return self.product.exists()

    class Meta:
        verbose_name = 'Carrito de compras'
        verbose_name_plural = 'Carritos de compras'
        db_table = 'cart'
        ordering = ['id_cart']

def set_identifier_cart(sender, instance, *args, **kwargs):
    """Funcion callback para agregar un identificador unico a cada instancia del carrito"""
    if not instance.identifier:
        identifier = str(uuid.uuid4())

        # Recorrer todos los carritos de compras para comprobar si ya existe el identificador unico
        while Cart.objects.filter(identifier = identifier).exists():
            identifier = str(uuid.uuid4())

        instance.identifier = identifier


pre_save.connect(set_identifier_cart, sender = Cart)

def update_total_cart(sender, instance, action, *args, **kwargs):
    """Funcion callback para actualizar el subtotal y total de la instancia del carrito de compras"""
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        instance.update_totals()

m2m_changed.connect(update_total_cart, sender = Cart.product.through)

class CartProductsManager(models.Manager):

    def create_or_update_quantity(self, cart, product, quantity = 1):
        objeto, created = self.get_or_create(cart = cart, product = product)

        if not created:
            quantity = objeto.quantity + quantity

        objeto.update_quantity(quantity)

        return objeto

class CartProducts(models.Model):
    cart = models.ForeignKey(Cart, verbose_name = 'Carrito de compras', on_delete = models.CASCADE)
    product = models.ForeignKey(Product, verbose_name = 'Producto', on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField('Cantidad', default = 1)
    create = models.DateTimeField('Fecha de creacion', auto_now_add = True)
    modified = models.DateTimeField('Fecha de modificacion', auto_now = True) 

    objects = CartProductsManager()

    def update_quantity(self, quantity = 1):
        self.quantity = quantity
        self.save()

def post_save_update_totals(sender, instance, *args, **kwargs):
    instance.cart.update_totals()

post_save.connect(post_save_update_totals, sender = CartProducts)