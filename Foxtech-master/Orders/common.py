from enum import Enum
from django.conf import settings
from django.template.loader import get_template
from django.shortcuts import reverse
from django.core.mail import EmailMultiAlternatives

class OrderStatus(Enum):
    CREATED = 'Creado'
    PAYED = 'Pagado'
    COMPLETED = 'Completado'
    CANCELED = 'Cancelado'

choices = [(item.value, item.value) for item in OrderStatus]

def send_bill_order(order, accounting_document):
    """
    Funcion de ayuda para enviar un correo con la factura despues de que se haya confirmado el pago del pedido.
    """

    template = get_template('mails/plantillaEnvioFactura.html')
    context = {
        'usuario': f"{order.user.first_name.split()[0]} {order.user.last_name.split()[0]}",
        'index': 'http://127.0.0.1:8000',
        'url': reverse('Orders:download-bill', kwargs={'number': accounting_document.number_accounting_document}),
        'orden': order,
    }
    content = template.render(context)

    email = EmailMultiAlternatives(
        subject = f'🛒 Factura orden de compra {order.identifier}',
        body = '',
        from_email = settings.EMAIL_HOST_USER,
        to = [order.user.email]
    )

    email.attach_alternative(content, 'text/html')
    email.send(fail_silently = False)

    order.send_bill = True
    order.save()