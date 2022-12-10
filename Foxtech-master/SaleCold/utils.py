from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
import threading

def send_email(url_template, context, subject, addressee, copy = None):
    """
    Funcion utilitaria para encapsular la logica de envio de correos para no repetir codigo.
    """

    template = get_template(url_template)

    content = template.render(context)

    email = EmailMultiAlternatives(
        subject = subject,
        body = '',
        from_email = settings.EMAIL_HOST_USER,
        to = [addressee],
        cc = [copy if copy != None else '']
    )

    email.attach_alternative(content, 'text/html')

    thread = threading.Thread(target = email.send(fail_silently = False))
    thread.start()