from django.db import models
from Orders.common import OrderStatus
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core import validators

class City(models.Model):
    id_city = models.AutoField("Id Ciudad", primary_key = True)
    description = models.CharField("Descripcion", null = True, blank = True, max_length=45)
    zip_code = models.CharField("Codigo postal", max_length = 6)
    create = models.DateTimeField('Fecha de creacion', auto_now_add = True)
    modified = models.DateTimeField('Fecha de modificacion', auto_now = True)
    state = models.BooleanField('Estado', default = True)

    def __str__(self):
        return self.description

    def length_zip_code(self):
        """Funcion complementaria para test unitarios"""
        return len(self.zip_code) <= 6

    class Meta:
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        db_table = "city"
        ordering = ['id_city']

class TypeOfDocument(models.Model):
    id_type_of_document = models.AutoField("Id tipo de documento", primary_key=True)
    description = models.CharField("Descripcion", max_length=45)
    create = models.DateTimeField('Fecha de creacion', auto_now_add = True)
    modified = models.DateTimeField('Fecha de modificacion', auto_now=True)
    state = models.BooleanField('Estado', default = True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documento"
        db_table = "type_of_document"
        ordering = ['id_type_of_document']

class UserManager(BaseUserManager):
    use_in_migrations = True

    def save_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('El correo debe ser ingresado')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self.save_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser should be True')
        
        extra_fields['is_staff'] = True

        return self.save_user(email, password, **extra_fields)

class UserModel(AbstractBaseUser, PermissionsMixin):
    MALE = 'Hombre'
    FEMALE = 'Mujer'
    OTHER = 'Prefiero no decirlo'
    GENDERS = [(MALE, 'Hombre'), (FEMALE, 'Mujer'), (OTHER, 'Prefiero no decirlo')]

    id_user = models.AutoField('Id usuario', primary_key = True)
    first_name = models.CharField('Nombre', max_length = 45, null = True)
    last_name = models.CharField('Apellido', max_length = 45, null = True)
    email = models.CharField('Correo', unique = True, max_length = 55, validators = [validators.EmailValidator()])
    type_of_document = models.ForeignKey(TypeOfDocument, verbose_name="Tipo de documento", on_delete=models.CASCADE, null = True)
    number_document = models.CharField("Numero de documento", max_length=12, null = True)
    main_address = models.CharField("Direccion", max_length=70, null = True)
    neighborhood = models.CharField("Barrio/Localidad", max_length = 30, null = True)
    city = models.ForeignKey(City, verbose_name="Ciudad", on_delete=models.CASCADE, null = True)
    phone_number = models.CharField("Numero de telefono", max_length=15, null = True)
    gender = models.CharField("Genero", choices=GENDERS, default=OTHER, max_length=19, null = True)
    create = models.DateTimeField('Fecha de creacion', auto_now_add = True)
    modified = models.DateTimeField('Fecha de modificacion', auto_now=True)

    is_staff = models.BooleanField('Administrador', default = False)
    is_active = models.BooleanField('Activo', default = True)

    # Especificar que campo sera el username
    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_orders_completed(self):
        return self.order_set.filter(state = OrderStatus.COMPLETED.value).order_by('-id_order')

    def get_orders_completed_and_canceled(self):
        return self.order_set.filter(Q(state = OrderStatus.COMPLETED.value) | Q(state = OrderStatus.CANCELED.value)).order_by('-id_order')

    def get_orders_payed(self):
        return self.order_set.filter(state = OrderStatus.PAYED.value).order_by('-id_order')

    def get_full_name(self):
        if self.first_name is None or self.last_name is None:
            return ''

        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        if self.first_name is None or self.last_name is None:
            return ''

        return f'{self.first_name.split()[0]} {self.last_name.split()[0]}'

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = "user"
        ordering = ['id_user']