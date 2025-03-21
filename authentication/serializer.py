from typing import Any, Dict
from rest_framework_simplejwt.settings import api_settings
from rest_framework import serializers
from authentication.models import User
import re
from rest_framework_simplejwt.tokens import RefreshToken

username_regex = r'^(?=.*[a-zA-Z])[a-zA-Z0-9_.-]{4,30}$'
email_regx = r'^[a-zA-Z0-9._]{2,30}@[a-zA-Z0-9.-]{2,30}\.[a-zA-Z]{2,30}$'
password_regx = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z0-9!@#$%^&*()_+=\-[\]{}|\\:;"\'<>,.?/~]{8,30}$'


class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField()

    class Meta:
        model = User
        fields = ('username',  'email', 'password',
                  'confirm_password')
        extra_kwargs = {'password': {'write_only': True},
                        'confirm_password': {'write_only': True}}

    def validate_username(self, value):
        if re.match(username_regex, value):
            return value
        else:
            raise serializers.ValidationError(
                'Username must be 4-30 characters long and can contain only alphanumeric values.'
            )

    def validate_email(self, value):
        if re.match(email_regx, value):
            return value
        else:
            raise serializers.ValidationError(
                'Enter a valid email address.'
            )

    def validate_password(self, value):
        if re.match(password_regx, value):
            return value
        else:
            raise serializers.ValidationError(
                'Enter a valid password.'
            )

    def validate_confirm_password(self, value):
        password = self.initial_data.get('password')
        if value == password:
            return value
        else:
            raise serializers.ValidationError(
                'Password mismatch.'
            )


class UserOtpVerificationSerializer(serializers.Serializer):
    otp = serializers.IntegerField()


class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate_password(self, value):
        if re.match(password_regx, value):
            return value
        else:
            raise serializers.ValidationError(
                'Enter a valid password.'
            )

    def validate_confirm_password(self, value):
        password = self.initial_data.get('password')
        if value == password:
            return value
        else:
            raise serializers.ValidationError(
                'Password mismatch.'
            )


class UserLoginSerializer(ForgotPasswordSerializer):
    password = serializers.CharField(write_only=True)


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        refresh = self.token_class(attrs["refresh"])

        user_id = refresh.payload.get('user_id')

        user = User.objects.get(id=user_id)

        # change line to manage the blocked user token refresh state
        # if user is not blocked

        role ='superuser' if user.is_superuser else 'user'

        refresh['role'] = role
        refresh['user'] = user.username
        refresh['is_blocked'] = user.is_blocked

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist  not in installed app, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

        return data
