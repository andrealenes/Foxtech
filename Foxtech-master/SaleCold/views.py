from django.shortcuts import render
from Products.models import Product
from Users.models import UserModel
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_GET
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib import messages
from django.shortcuts import redirect
from Products.models import Category
from django.views.generic import TemplateView
from .utils import send_email

@require_GET
def index(request):
    categorias = Category.objects.all()
    productos = Product.objects.filter(discount__gt = 0, stock__gt = 0).order_by('-discount')[:14]

    return render( request, 'index.html', context={
        'productos': productos,
        'categorias': categorias,
    } )

class InfoTemplateView(TemplateView):
    """
    Class view encargada de mostrar el template de informacion del aplicativo.
    """
    template_name = 'info.html'

@require_http_methods(['GET', 'POST'])
def reset_password(request):
    form = PasswordResetForm(request.POST or None)

    if request.method == 'POST':
        email = request.POST.get('email')
        user = UserModel.objects.filter(email = email).first()

        if user:
            try:
                template = 'mails/plantillaRecuperarContraseña.html'
                context = {
                    'usuario': f'{user.first_name.split()[0]} {user.last_name.split()[0]}',
                    'dominio': get_current_site(request).domain,
                    'uuid':  str(urlsafe_base64_encode(force_bytes(user.pk))),
                    'token': default_token_generator.make_token(user),
                }

                send_email(template, context, 'Recuperar contraseña', email)

                messages.success(request, 'Le enviamos las instrucciones por correo electrónico para configurar su nueva contraseña')

                return redirect('reset_password')
            except:
                messages.error(request, 'Error no se pudo enviar el correo electronico, por favor intente mas tarde')

        else:
            messages.error(request, 'Error el usuario no esta registrado en el sistema.')
        

    return render(request, 'users/restablecer_contraseña/recuperar_contraseña.html', context = {
        'form': form
    })