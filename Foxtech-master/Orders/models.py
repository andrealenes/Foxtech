from django.db import models
from Products.models import Product
from Users.models import UserModel
from Users.models import City
from enum import Enum
from Carts.models import Cart
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from .common import OrderStatus
from .common import choices
import uuid
from .common import send_bill_order

STATE = 'Estado'
DATE_CREATE = 'Fecha de creacion'
DATE_MODIFIED = 'Fecha de modificacion'

class TypeOfDelivery(models.Model):
    id_type_of_delivery = models.AutoField('Id tipo de entrega', primary_key = True)
    description = models.CharField('Descripcion', max_length=45)
    create = models.DateTimeField(DATE_CREATE, auto_now_add = True)
    modified = models.DateTimeField(DATE_MODIFIED, auto_now = True)
    state = models.BooleanField(STATE, default = True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Tipo de entrega'
        verbose_name_plural = 'Tipos de entregas'
        db_table = 'type_of_delivery'
        ordering = ['id_type_of_delivery']

class TypeAccountingDocument(models.Model):
    id_type_accounting_document = models.AutoField('Id tipo documento contable', primary_key = True)
    nature = models.CharField('Naturaleza', max_length=45)
    create = models.DateTimeField(DATE_CREATE, auto_now_add = True)
    modified = models.DateTimeField(DATE_MODIFIED, auto_now = True)
    state = models.BooleanField(STATE, default = True)

    def __str__(self):
        return self.nature

    class Meta:
        verbose_name = 'Tipo documento contable'
        verbose_name_plural = 'Tipos documentos contables'
        db_table = 'type_accounting_document'
        ordering = ['id_type_accounting_document']

class PaymentType(models.Model):
    id_payment_type = models.AutoField('Id tipo de pago', primary_key= True)
    description = models.CharField('Descripcion', max_length=45)
    create = models.DateTimeField(DATE_CREATE, auto_now_add = True)
    modified = models.DateTimeField(DATE_MODIFIED, auto_now = True)
    state = models.BooleanField(STATE, default = True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Tipo de pago'
        verbose_name_plural = 'Tipos de pagos'
        db_table = 'payment_type'
        ordering = ['id_payment_type']

class Address(models.Model):
    id_address = models.AutoField('Id direccion', primary_key = True)
    user = models.ForeignKey(UserModel, verbose_name = 'Usuario', on_delete = models.CASCADE)
    city = models.ForeignKey(City, verbose_name = 'Ciudad', on_delete = models.CASCADE)
    address = models.CharField('Direccion', max_length = 70)
    neighborhood = models.CharField("Barrio/Localidad", max_length = 50)
    default = models.BooleanField('Direccion principal', default = False)
    create = models.DateTimeField(DATE_CREATE, auto_now_add = True)
    modified = models.DateTimeField(DATE_MODIFIED, auto_now = True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Direccion de envio'
        verbose_name_plural = 'Direcciones de envio'
        db_table = 'address'
        ordering = ['id_address']

class Order(models.Model):
    id_order = models.AutoField('Id orden', primary_key = True)
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha pedido')
    type_of_delivery = models.ForeignKey(TypeOfDelivery, verbose_name='Tipo de entrega', on_delete = models.CASCADE, null = True, blank = True)
    type_accounting_document = models.ForeignKey(TypeAccountingDocument, verbose_name='Tipo documento contable', on_delete = models.CASCADE,  null = True, blank = True)
    payment_type = models.ForeignKey(PaymentType, verbose_name='Tipo de pago', on_delete = models.CASCADE,  null = True, blank = True)
    user = models.ForeignKey(UserModel, verbose_name='Cliente', on_delete=models.CASCADE)
    state = models.CharField(STATE, choices = choices, default = OrderStatus.CREATED.value, max_length = 10)
    cart = models.ForeignKey(Cart, verbose_name = 'Carrito', on_delete = models.CASCADE)
    total = models.PositiveIntegerField('Total', default = 0)
    shipping_total = models.PositiveIntegerField('Costo envio', default = 0)
    modified = models.DateTimeField(DATE_MODIFIED, auto_now = True)
    identifier = models.CharField('Identificador unico' , unique = True, max_length = 100)
    address = models.ForeignKey(Address, verbose_name = 'Direccion', null = True, blank = True, on_delete=models.CASCADE)
    send_bill = models.BooleanField('Factura enviada', default = False)

    def __str__(self):
        return self.identifier

    def get_total(self):
        """
        Funcion para obtener el total de la orden.
        """

        return self.cart.total + self.shipping_total

    def update_total(self):
        """
        Funcion para actualizar el total de la orden.
        """

        self.total = self.get_total()
        self.save()

    def cancel(self):
        """
        Funcion para cambiar el estado de la orden a cancelado.
        """

        self.state = OrderStatus.CANCELED.value
        self.save()

    def completed(self):
        """
        Funcion para cambiar el estado de la orden a completado.
        """

        self.state = OrderStatus.COMPLETED.value
        self.save()

    def payed(self):
        """
        Funcion para cambiar el estado de la orden a pagado.
        """

        self.state = OrderStatus.PAYED.value
        self.save()

    def get_total_quantity_products(self):
        """
        Funcion para obtener la cantidad total de productos asociados a la orden.
        """

        total = [producto.quantity for producto in self.cart.cartproducts_set.all()]
        return sum(total)

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Ordenes'
        db_table = 'order'
        ordering = ['id_order']

def set_identifier_order(sender, instance, *args, **kwargs):
    """
    Funcion callback para agregar un identificador unico a cada instancia de order
    """

    if not instance.identifier:
        identifier = str(uuid.uuid4())

        # Recorrer todos los carritos de compras para comprobar si ya existe el identificador unico
        while Order.objects.filter(identifier = identifier).exists():
            identifier = str(uuid.uuid4())

        instance.identifier = identifier


pre_save.connect(set_identifier_order, sender = Order)

def set_total_order(sender, instance, *args, **kwargs):
    """
    Callback para cambiar el valor del total de la orden antes de guardar una instancia en la base de datos.
    """

    instance.total = instance.get_total()

pre_save.connect(set_total_order, sender = Order)

def callback_send_bill(sender, instance, *args, **kwargs):
    """
    Callback para realizar el llamado a la funcion que se encargara de enviar la factura una vez el administrador haya confirmado el pago.
    """

    if instance.state == OrderStatus.PAYED.value and instance.send_bill == False:
        accounting_document = AccountingDocument.objects.create(order = instance)
        send_bill_order(instance, accounting_document)

post_save.connect(callback_send_bill, sender = Order)

class AccountingDocument(models.Model):
    id_accounting_document = models.AutoField('Id documento contable', primary_key = True)
    number_accounting_document = models.CharField('Numero documento contable', max_length = 10, unique = True)
    order = models.OneToOneField(Order, on_delete = models.CASCADE, verbose_name = 'Orden')
    accounting_document_date = models.DateTimeField(auto_now_add=True, verbose_name='Fecha documento contable')

    class Meta:
        verbose_name = 'Documento contable'
        verbose_name_plural = 'Documentos contables'
        db_table = 'accounting_document'
        ordering = ['id_accounting_document']

def set_number_accounting_document(sender, instance, *args, **kwargs):
    """
    Callback para generar un numero unico de factura.
    """

    if not instance.number_accounting_document:
        number = str(int(uuid.uuid4()))[:10]

        while AccountingDocument.objects.filter(number_accounting_document=number).exists():
            number = str(int(uuid.uuid4()))[:10]

        instance.number_accounting_document = number

pre_save.connect(set_number_accounting_document, sender = AccountingDocument)