from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from authentication.models import *
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils import timezone


def generate_otp_and_validity():
    otp = get_random_string(length=6, allowed_chars='9876543210')
    valid_until = timezone.now() + timedelta(minutes=10)
    return otp, valid_until


def generate_uid_and_token(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token


def checkuidtoken(uid, token):
    try:
        pk = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=pk)
        verify_otp = Link.objects.get(
            user=user, uid=uid, token=token, otp__isnull=False)
        return user, verify_otp
    except Exception:
        return None, None


def checkpassuidtoken(uid, token):
    try:
        pk = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=pk)
        verify_link = Link.objects.get(
            user=user, uid=uid, token=token, password_reset=True, valid_until__gte=timezone.now())
        return user, verify_link
    except Exception:
        return None, None
