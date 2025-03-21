from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


@shared_task(bind=True)
def send_verification_email(self, subject, uid, token, valid_until,  username, email, otp=None):
    emailcontext = {
        'subject': subject,
        'valid_until': valid_until,
        'otp': otp,
        'username': username,
        'uid': uid,
        'token': token,
        'domain': settings.CORS_ALLOWED_ORIGINS[0]

    }
    message = render_to_string('verification_email.html', emailcontext)
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email,]

    email = EmailMessage(subject, message, from_email, recipient_list)
    email.content_subtype = 'html'
    email.send(fail_silently=True)
