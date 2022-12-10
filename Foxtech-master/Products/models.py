from django.db import models
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator 
from django.utils.text import slugify
from django.db.models.signals import pre_save
import uuid

FECHA_CREACION = 'Fecha de creacion'
FECHA_MODIFICACION = 'Fecha de modificacion'
ESTADO = 'Estado'

class UnitOfMeasure(models.Model):
    id_unit_of_measure = models.AutoField("Id unidad de medida", primary_key = True)
    name = models.CharField("Nombre unidad de medida", max_length = 45)
    create = models.DateTimeField(FECHA_CREACION, auto_now_add = True)
    modified = models.DateTimeField(FECHA_MODIFICACION, auto_now=True)
    state = models.BooleanField(ESTADO, default = True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Unidad de medida"
        verbose_name_plural = "Unidades de medidas"
        db_table = "unit_of_measure"
        ordering = ['id_unit_of_measure']

class Product(models.Model):
    id_product = models.AutoField("Id producto", primary_key = True)
    name = models.CharField("Nombre producto", max_length = 55)
    description = models.TextField("Descripcion", null = True, blank = True)
    image = models.URLField("Imagen del producto")
    unit_price = models.PositiveIntegerField("Precio unitario", default = 0)
    final_price = models.PositiveIntegerField("Precio final", default = 0)
    reference = models.CharField("Codigo", null=True, blank=True, max_length=10)
    inputs = models.PositiveIntegerField('Entradas', default = 0)
    outputs = models.PositiveIntegerField('Salidas', default = 0)
    stock = models.PositiveSmallIntegerField("Stock", null = True, blank = True, default = 0)
    discount = models.PositiveSmallIntegerField("Descuento", null = True, blank = True, default = 0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    unit_of_measure = models.ForeignKey(UnitOfMeasure, verbose_name = "Unidad de medida", on_delete = models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True, verbose_name='Ruta')
    create = models.DateTimeField(FECHA_CREACION, auto_now_add = True)
    modified = models.DateTimeField(FECHA_MODIFICACION, auto_now=True)
    state = models.BooleanField(ESTADO, default = True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        db_table = "product"
        ordering = ['id_product']

def set_slug_product(sender, instance, *args, **kwargs):
    """
    Callback para agregar un slug unico a cada instancia del producto antes de guardarlo en la base de datos.
    """

    if instance.name and not instance.slug:
        # Crea un slug con el nombre del producto
        slug = slugify(instance.name)

        # Crear una consulta a la base de datos para revisar si el slug ya existe, si existe entonces creamos un nuevo slug
        while Product.objects.filter(slug = slug).exists():
            slug = slugify(
                f'{instance.name}-{str(uuid.uuid4())[:8]}'
            )
        
        instance.slug = slug

def set_reference_product(sender, instance, *args, **kwargs):
    """
    Callback para agregar un codigo de referencia unico para cada instancia del producto antes de guardarlo en la base de datos.
    """

    reference = str(uuid.uuid4())[:10]

    if not instance.reference:
        # Crear el codigo de referencia unico
        while Product.objects.filter(reference = reference).exists():
            reference = str(uuid.uuid4())[:10]

        instance.reference = reference

def set_final_price_product(sender, instance, *args, **kwargs):
    """
    Callback para calcular el precio final del producto antes de guardar.
    """

    unit_price = instance.unit_price

    if instance.discount == 0:
        instance.final_price = unit_price
    else:
        instance.final_price = round(abs(unit_price * (instance.discount / 100) - unit_price))

def set_stock_product(sender, instance, *args, **kwargs):
    """
    Callback para modificar el stock de los productos antes de guardarlos en la base de datos, el campo stock es calculado ya que es la diferencia entre los campos entradas y salidas.
    """
    
    if instance.outputs > instance.inputs:
        instance.stock = 0
    else:
        instance.stock = abs(instance.outputs - instance.inputs)

# Conectar los callbacks con el modelo Product
pre_save.connect(set_slug_product, sender = Product)
pre_save.connect(set_reference_product, sender = Product)
pre_save.connect(set_final_price_product, sender = Product)
pre_save.connect(set_stock_product, sender = Product)

class Category(models.Model):
    id_category = models.AutoField("Id categoria", primary_key = True)
    name = models.CharField("Nombre categoria", max_length = 55)
    description = models.CharField("Descripcion", null = True, blank = True, max_length = 255)
    slug = models.SlugField(unique=True, null=True, blank=True, verbose_name='Ruta')
    products = models.ManyToManyField(Product, verbose_name='Productos')
    create = models.DateTimeField(FECHA_CREACION, auto_now_add = True)
    modified = models.DateTimeField(FECHA_MODIFICACION, auto_now=True)
    state = models.BooleanField(ESTADO, default = True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        db_table = "category"
        ordering = ['id_category']

    @classmethod
    def create(cls, id_category, name, description):
        category = cls(id_category = id_category, name = name, description = description)
        return category

def set_slug_category(sender, instance, *args, **kwargs):
    """
    Callback para asignar un slug unico a la categoria antes de guardar la instancia.
    """
    if instance.name and not instance.slug:
        slug = slugify(instance.name)

        while Category.objects.filter(slug = slug).exists():
            slug = slugify(
                f'{instance.name}-{str(uuid.uuid4())[:8]}'
            )

        instance.slug = slug
    

# Conectar el callback con el modelo Category
pre_save.connect(set_slug_category, sender=Category)