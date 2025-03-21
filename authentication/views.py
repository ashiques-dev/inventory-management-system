from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.task import *
from authentication.models import *
from authentication.serializer import *
from authentication.utils import *


class UserRegistrationView(APIView):
    def post(self, request, role):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.validated_data.pop('confirm_password', None)

        user = User.objects.create_user(**serializer.validated_data)

        user.save()

        otp, valid_until = generate_otp_and_validity()
        uid, token = generate_uid_and_token(user)

        subject = 'Account verification mail'

        send_verification_email.delay(
            subject, uid, token, valid_until,  user.username, user.email, otp)

        Link.objects.create(
            user=user, uid=uid,  token=token, otp=otp, valid_until=valid_until)

        return Response({"message": 'Your account has been successfully created. Please check your email to verify your account.'}, status=status.HTTP_201_CREATED)


class OtpVerifyView(APIView):

    def get(self, request, uid, token):
        user, verify_otp = checkuidtoken(uid, token)
        if not (user and verify_otp):
            return Response({'message': "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Good to go.'}, status=status.HTTP_200_OK)

    def post(self, request, uid, token):
        user, verify_otp = checkuidtoken(uid, token)
        if not (user and verify_otp):
            return Response({'message': "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST)

        if not verify_otp.valid_until >= timezone.now():
            return Response({"message": 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserOtpVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = serializer.validated_data['otp']

        if verify_otp.otp == otp:
            user.is_verified = True
            user.save()
            verify_otp.delete()
            return Response({'message': 'User successfully verified', }, status=status.HTTP_200_OK)
        else:
            return Response({"message": 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


class ResendOtpView(APIView):
    def get(self, request, uid, token):
        user, verify_otp = checkuidtoken(uid, token)
        if not (user and verify_otp):
            return Response({'message': "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST)

        otp, valid_until = generate_otp_and_validity()

        subject = 'Account verification mail'

        send_verification_email.delay(
            subject, uid, token, valid_until,  user.username, user.email, otp)

        verify_otp.otp = otp
        verify_otp.valid_until = valid_until
        verify_otp.save()
        return Response({"message": 'OTP successfully resend. Please check your email.'}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        try:
            user = None
            if '@' in username:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)

        except:
            return Response({'message': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        valid_until = timezone.now() + timedelta(minutes=20)
        uid, token = generate_uid_and_token(user)

        subject = 'Password reset mail'

        send_verification_email.delay(
            subject, uid, token, valid_until,  user.username, user.email)

        reset_link, created = Link.objects.get_or_create(user=user, password_reset=True, defaults={
                                                         'token': token, 'valid_until': valid_until, 'uid': uid})

        if not created:
            reset_link.uid = uid
            reset_link.token = token
            reset_link.valid_until = valid_until
            reset_link.save()

        pos = 'superuser' if user.is_superuser else 'user'

        return Response({'pos': pos}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def get(self, request, uid, token):
        user, verify_link = checkpassuidtoken(uid, token)
        if not (user and verify_link):
            return Response({'message': "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Good to go.'}, status=status.HTTP_200_OK)

    def post(self, request, uid, token):
        user, verify_link = checkpassuidtoken(uid, token)
        if not (user and verify_link):
            return Response({'message': "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data['password']

        user.set_password(password)
        user.save()
        verify_link.delete()
        pos = 'superuser' if user.is_superuser else 'user'
        return Response({'pos': pos}, status=status.HTTP_200_OK)


class UserLoginView(APIView):
    def post(self, request, role):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        try:
            if '@' in username:
                temp_user = User.objects.get(email=username)
                username = temp_user.username
        except:
            return Response({"message": 'Invalid user credentials'}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(username=username, password=password)

        if user is not None:
            data = {}
            pos = 'superuser' if user.is_superuser else 'user'

            if role != pos:
                data['pos'] = False

            elif not user.is_verified:
                otp, valid_until = generate_otp_and_validity()
                uid, token = generate_uid_and_token(user)

                subject = 'New Account verification mail'
                send_verification_email.delay(
                    subject, uid, token, valid_until,  user.username, user.email, otp)

                user_otp, created = Link.objects.get_or_create(user=user, password_reset=False, defaults={
                                                               'otp': otp, 'token': token, 'valid_until': valid_until, 'uid': uid})

                if not created:
                    user_otp.otp = otp
                    user_otp.uid = uid
                    user_otp.token = token
                    user_otp.valid_until = valid_until
                    user_otp.save()

                data['notverified'] = True

            elif user.is_blocked:
                data['is_blocked'] = True

            else:
                login(request, user)
                refresh = RefreshToken.for_user(user)

                refresh['role'] = role
                refresh['user'] = user.username
                refresh['is_blocked'] = False

                data['role'] = role
                data['refresh'] = str(refresh)
                data['access'] = str(refresh.access_token)

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"message": 'Invalid user credentials'}, status=status.HTTP_404_NOT_FOUND)


class CustomTokenRefreshView(APIView):
    def post(self, request):
        serializer = CustomTokenRefreshSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            print(e)
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data)
