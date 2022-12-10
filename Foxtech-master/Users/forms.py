from django import forms
from Users.models import City
from Users.models import TypeOfDocument
from Users.models import UserModel
from django.contrib.auth import authenticate
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import reverse
from Orders.models import Address
from SaleCold.utils import send_email

CAMPO_OBLIGATORIO = 'Este campo es obligatorio.'
ERROR_CANTIDAD_CARACTERES = 'Este campo acepta minimo 4 caracteres y maximo 25 caracteres.'
GENDER = (
    (1, 'Genero'),
    (2, 'Hombre'),
    (3, 'Mujer'),
    (4, 'Prefiero no decirlo'),
)

class RegisterForm(forms.Form):
    nombre = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
                'autofocus': 'True',
                'class': 'form-register__input',
                'placeholder': 'Nombre'
        })
    )
    apellido = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'form-register__input',
            'placeholder': 'Apellido'
        })
    )
    numero_documento = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'placeholder': 'Numero de documento',
            'class': 'form-register__input'
        })
    )
    direccion = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'placeholder': 'Direccion de residencia',
            'class': 'form-register__input'
        })
    )
    telefono = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'placeholder': 'Numero telefonico',
            'class': 'form-register__input',
            'type': 'tel'
        })
    )
    email = forms.EmailField(
        required = False,
        widget = forms.TextInput(attrs = {
            'placeholder': 'Correo',
            'class': 'form-register__input'
        })
    )
    contrasena = forms.CharField(
        required = False,
        widget = forms.PasswordInput(attrs = {
            'placeholder': 'Contraseña',
            'class': 'form-register__input'
        })
    )
    ciudad = forms.ModelChoiceField(
        required = False,
        widget = forms.Select(attrs = {
            'class': 'container-select-register',
        }),
        queryset = City.objects.all(),
        empty_label = "Ciudad",
    )

    tipo_documento = forms.ModelChoiceField(
        required = False,
        widget = forms.Select(attrs = {
            'class': 'container-select-register',
        }),
        queryset = TypeOfDocument.objects.all(),
        empty_label = 'Tipo de documento',
    )

    genero = forms.TypedChoiceField(
        required = False,
        widget = forms.Select(attrs = {
            'class': 'container-select-register',
            'placeholder': 'Genero',
        }),
        empty_value = '1',
        choices = GENDER,
    )
    barrio = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'form-register__input',
            'placeholder': 'Barrio/Localidad',
        })
    )
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if len(nombre) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(nombre) < 4 or len(nombre) > 25:
            raise forms.ValidationError(ERROR_CANTIDAD_CARACTERES)

        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')

        if len(apellido) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(apellido) < 4 or len(apellido) > 25:
            raise forms.ValidationError(ERROR_CANTIDAD_CARACTERES)

        return apellido

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if UserModel.objects.filter(email = email).exists():
            raise forms.ValidationError('El usuario ya esta registrado en el sistema.')
        elif len(email) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return email

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if len(direccion) > 30:
            raise forms.ValidationError('Este campo acepta maximo 30 caracteres.')
        elif len(direccion) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return direccion

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento')

        if len(numero_documento) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(numero_documento) > 12:
            raise forms.ValidationError('Este campo acepta maximo 12 caracteres')
        
        return numero_documento

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if len(telefono) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(telefono) < 9 or len(telefono) > 15:
            raise forms.ValidationError('Este campo acepta minimo 4 caracteres y maximo 15 caracteres.')

        return telefono

    def clean_contrasena(self):
        contrasena = self.cleaned_data.get('contrasena')
        mayusculas = 0
        numeros = 0
        simbolos = 0

        for caracter in contrasena:
            if caracter in "!#$%&'()*+,-./:;=?{|}~[\]^_`@·½¬><":
                simbolos += 1
            elif caracter in '0123456789':
                numeros += 1
            elif caracter == caracter.upper():
                mayusculas += 1

        if len(contrasena) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif mayusculas < 1 or numeros < 1 or simbolos < 1:
            raise forms.ValidationError('La contraseña debe tener minimo 8 caracteres y debe estar compuesta por 1 simbolo, 1 mayuscula y 1 numero.')

        return contrasena
    
    def clean_ciudad(self):
        ciudad = self.cleaned_data.get('ciudad')

        if ciudad == None:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return ciudad

    def clean_tipo_documento(self):
        tipo_documento = self.cleaned_data.get('tipo_documento')

        if tipo_documento == None:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        
        return tipo_documento

    def clean_genero(self):
        genero = self.cleaned_data.get('genero')

        if genero == '1':
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        
        return genero

    def clean_barrio(self):
        barrio = self.cleaned_data.get('barrio')

        if len(barrio) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(barrio) > 50:
            raise forms.ValidationError('Este campo acepta maximo 50 caracteres')

        return barrio

    def save(self):
        user = UserModel.objects.create_user(
            email = self.cleaned_data.get('email').strip(),
            password = self.cleaned_data.get('contrasena'),
        )

        user.first_name = self.cleaned_data.get('nombre').strip()
        user.last_name = self.cleaned_data.get('apellido').strip()
        user.type_of_document = TypeOfDocument.objects.get(
            description = self.cleaned_data.get('tipo_documento')
        )
        user.number_document = self.cleaned_data.get('numero_documento').strip()
        user.main_address = self.cleaned_data.get('direccion').strip()
        user.neighborhood = self.cleaned_data.get('barrio').strip()
        user.phone_number = self.cleaned_data.get('telefono').strip()
        user.city = City.objects.get(description = self.cleaned_data.get('ciudad'))
        user.gender = self.cleaned_data.get('genero').strip()

        user.save()

        # Crear la direccion de envio apenas el usuario se registra.
        Address.objects.create(
            user = user,
            city = City.objects.get(description = self.cleaned_data.get('ciudad')),
            address = self.cleaned_data.get('direccion').strip(),
            default = True,
            neighborhood = self.cleaned_data.get('barrio').strip()
        )

        return user

    def send(self, request):
        template = 'mails/plantillaBienvenida.html'
        context = {
            'usuario': f"{self.cleaned_data.get('nombre').strip().split()[0]} {self.cleaned_data.get('apellido').strip().split()[0]}",
            'dominio': get_current_site(request).domain,
            'url': reverse('index'),
        }
        email = self.cleaned_data.get('email').strip()

        send_email(template, context, 'Bienvenid@ a FoxTech', email)


class ContactForm(forms.Form):
    nombre = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'tab-index': 1,
            'class': 'form-contact__input',
            'placeholder': 'Nombre',
            'autofocus': 'True'
        }),
        
    )
    apellido = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'tab-index': 2,
            'class': 'form-contact__input',
            'placeholder': 'Apellido',
        })
    )
    telefono = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'tab-index': 3,
            'class': 'form-contact__input',
            'placeholder': 'Telefono',
            'type': 'tel'
        })
    )
    correo = forms.EmailField(
        required = False,
        widget = forms.TextInput(attrs = {
            'tab-index': 4,
            'class': 'form-contact__input',
            'placeholder': 'Correo electronico',
        })
    )
    asunto = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'tab-index': 5,
            'class': 'form-contact__input',
            'placeholder': 'Asunto',
        })
    )
    mensaje = forms.CharField(
        required = False,
        widget = forms.Textarea(attrs = {
            'tab-index': 6,
            'class': 'form-contact__textarea',
            'placeholder': 'Mensaje',
        })
    )

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if len(nombre) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(nombre) < 4 or len(nombre) > 25:
            raise forms.ValidationError(ERROR_CANTIDAD_CARACTERES)

        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')

        if len(apellido) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(apellido) < 4 or len(apellido) > 25:
            raise forms.ValidationError(ERROR_CANTIDAD_CARACTERES)

        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if len(telefono) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(telefono) < 9 or len(telefono) > 15:
            raise forms.ValidationError('Este campo acepta minimo 9 caracteres y maximo 15 caracteres.')

        return telefono

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')

        if len(correo) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return correo

    def clean_asunto(self):
        asunto = self.cleaned_data.get('asunto')

        if len(asunto) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(asunto) < 5 or len(asunto) > 30:
            raise forms.ValidationError('Este campo acepta minimo 5 caracteres y maximo 30 caracteres.')

        return asunto

    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje')

        if len(mensaje) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return mensaje

    def send(self, request):
        template = 'mails/plantillaContacto.html'
        context = {
            'nombre': f"{self.cleaned_data.get('nombre').strip()} {self.cleaned_data.get('apellido').strip()}",
            'asunto': self.cleaned_data.get('asunto').strip(),
            'correo': self.cleaned_data.get('correo').strip(),
            'telefono': self.cleaned_data.get('telefono').strip(),
            'mensaje': self.cleaned_data.get('mensaje').strip(),
            'dominio': get_current_site(request).domain,
            'url': reverse('index')
        }

        send_email(template, context, 'Nuevo mensaje de contacto', settings.EMAIL_HOST_USER, 'adlenes8@misena.edu.co')
        
class UpdateDataUserForm(forms.Form):
    nombre = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'container-label-form__input',
            'autofocus': 'True',
        })
    )

    apellido = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'container-label-form__input',
        })
    )

    tipo_documento = forms.ModelChoiceField(
        required = False,
        widget = forms.Select(attrs = {
            'class': 'container-select-update-user',
        }),
        queryset = TypeOfDocument.objects.all(),
    )

    numero_documento = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'container-label-form__input',
        })
    )

    ciudad = forms.ModelChoiceField(
        required = False,
        widget = forms.Select(attrs = {
            'class': 'container-select-update-user',
        }),
        queryset = City.objects.all(),
    )

    direccion = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'container-label-form__input',
        })
    )

    correo = forms.EmailField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'container-label-form__input',
        })
    )

    telefono = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'container-label-form__input',
            'type': 'tel'
        })
    )

    barrio = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'container-label-form__input',
        })
    )

    genero = forms.TypedChoiceField(
        required = False,
        widget = forms.Select(attrs = {
            'class': 'container-select-update-user',
        }),
        empty_value = '1',
        choices = GENDER,
    )

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if len(nombre) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(nombre) < 4 or len(nombre) > 25:
            raise forms.ValidationError(ERROR_CANTIDAD_CARACTERES)

        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')

        if len(apellido) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(apellido) < 4 or len(apellido) > 25:
            raise forms.ValidationError(ERROR_CANTIDAD_CARACTERES)

        return apellido

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')

        if len(correo) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return correo

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')

        if len(direccion) > 70:
            raise forms.ValidationError('Este campo acepta maximo 70 caracteres.')
        elif len(direccion) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return direccion

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento')

        if len(numero_documento) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        
        return numero_documento

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if len(telefono) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(telefono) < 9 or len(telefono) > 15:
            raise forms.ValidationError('Este campo acepta minimo 9 caracteres y maximo 15 caracteres.')

        return telefono
    
    def clean_ciudad(self):
        ciudad = self.cleaned_data.get('ciudad')

        if ciudad == None:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return ciudad

    def clean_tipo_documento(self):
        tipo_documento = self.cleaned_data.get('tipo_documento')

        if tipo_documento == None:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        
        return tipo_documento

    def clean_barrio(self):
        barrio = self.cleaned_data.get('barrio')

        if len(barrio) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(barrio) > 50:
            raise forms.ValidationError('Este campo acepta maximo 50 caracteres')

        return barrio

    def clean_genero(self):
        genero = self.cleaned_data.get('genero')

        if genero == '1':
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        
        return genero

    def save(self, user):
        user.first_name = self.cleaned_data.get('nombre').strip()
        user.last_name = self.cleaned_data.get('apellido').strip()
        user.email = self.cleaned_data.get('correo').strip()
        user.username = self.cleaned_data.get('correo').strip()
        user.save()

        user.city = City.objects.get(
            description = self.cleaned_data.get('ciudad')
        )
        user.type_of_document = TypeOfDocument.objects.get(
            description = self.cleaned_data.get('tipo_documento')
        )
        user.number_document = self.cleaned_data.get('numero_documento').strip()
        user.address = self.cleaned_data.get('direccion').strip()
        user.phone_number = self.cleaned_data.get('telefono').strip()
        user.gender = self.cleaned_data.get('genero')
        user.neighborhood = self.cleaned_data.get('barrio').strip()

        user.save()

        direccion = Address.objects.get(user = user, default = True)
        nueva_direccion = self.cleaned_data.get('direccion').strip()

        # Verificar si la direccion actual del usuario es distinta a la nueva direccion, si es asi entonces se actualiza.
        if direccion != nueva_direccion:
            if Address.objects.filter(user = user, default = False, address = nueva_direccion).exists():
                Address.objects.filter(user = user, default = False, address = nueva_direccion).delete()
            direccion.address = self.cleaned_data.get('direccion').strip()
            direccion.save()

class LoginForm(forms.Form):
    correo = forms.EmailField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'form-login__input',
            'autofocus': 'true',
            'tab-index': 1,
            'placeholder': 'Correo'
        })

    )
    contrasena = forms.CharField(
        required = False,
        widget = forms.PasswordInput(attrs = {
            'class': 'form-login__input',
            'tab-index': 2,
            'placeholder': 'Contraseña'
        })
    )

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')

        if len(correo) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return correo

    def clean_contrasena(self):
        contrasena = self.cleaned_data.get('contrasena')

        if len(contrasena) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return contrasena

    def authenticate_user(self):
        correo = self.cleaned_data.get('correo').strip()
        contrasena = self.cleaned_data.get('contrasena')

        return authenticate(email = correo, password = contrasena)

class ChangePassword(forms.Form):
    contrasena = forms.CharField(
        required = False,
        widget = forms.PasswordInput(attrs = {
            'autofocus': 'true',
            'tab-index': 1,
            'class': 'container-label-form-contraseña__input',
        })
    )

    contrasena2 = forms.CharField(
        required = False,
        widget = forms.PasswordInput(attrs = {
            'tab-index': 2,
            'class': 'container-label-form-contraseña__input',
        })
    )

    def clean_contrasena(self):
        contrasena = self.cleaned_data.get('contrasena')
        mayusculas = 0
        numeros = 0
        simbolos = 0

        for caracter in contrasena:
            if caracter in "!#$%&'()*+,-./:;=?{|}~[\]^_`@·½¬><":
                simbolos += 1
            elif caracter in '0123456789':
                numeros += 1
            elif caracter == caracter.upper():
                mayusculas += 1

        if len(contrasena) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif mayusculas < 1 or numeros < 1 or simbolos < 1:
            raise forms.ValidationError('La contraseña debe tener minimo 8 caracteres y debe estar compuesta por 1 simbolo, 1 mayuscula y 1 numero.')

        return contrasena

    def clean(self):
        cleaned_data = super().clean()

        if len(cleaned_data.get('contrasena2')) == 0:
            self.add_error('contrasena2', CAMPO_OBLIGATORIO)
        elif cleaned_data.get('contrasena2') != cleaned_data.get('contrasena'):
            self.add_error('contrasena2', 'Las contraseñas deben coincidir.')

class AddressForm(forms.Form):
    ciudad = forms.ModelChoiceField(
        required = False,
        widget = forms.Select(attrs = {
            'class': 'container-label-address-user__select',
        }),
        queryset = City.objects.all(),
        empty_label = 'Ciudad'
    )
    direccion = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'container-label-address-user__input',
        })
    )
    barrio = forms.CharField(
        required = False,
        widget = forms.TextInput(attrs = {
            'class': 'container-label-address-user__input',
        })
    )
    defecto = forms.ChoiceField(
        required = False,
        widget = forms.Select(attrs = {
            'class': 'container-label-address-user__select',
        }),
        choices = (
            ('1', 'Seleccionar'),
            ('2', 'Si'),
            ('3', 'No'),
        )
    )

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')

        if len(direccion) > 70:
            raise forms.ValidationError('Este campo acepta maximo 70 caracteres.')
        elif len(direccion) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return direccion

    def clean_ciudad(self):
        ciudad = self.cleaned_data.get('ciudad')

        if ciudad == None:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return ciudad

    def clean_barrio(self):
        barrio = self.cleaned_data.get('barrio')

        if len(barrio) == 0:
            raise forms.ValidationError(CAMPO_OBLIGATORIO)
        elif len(barrio) > 50:
            raise forms.ValidationError('Este campo acepta maximo 50 caracteres')

        return barrio

    def clean_defecto(self):
        defecto = self.cleaned_data.get('defecto')

        if defecto == '1':
            raise forms.ValidationError(CAMPO_OBLIGATORIO)

        return defecto

    def save(self, pk, user):
        direccion = Address.objects.get(pk = pk, user = user)
        direccion.city = City.objects.get(description = self.cleaned_data.get('ciudad'))
        direccion.address = self.cleaned_data.get('direccion')
        direccion.neighborhood = self.cleaned_data.get('barrio')
        direccion.default = True if self.cleaned_data.get('defecto') == '2' else False
        try:
            direccion.save()
            return direccion
        except:
            return False
