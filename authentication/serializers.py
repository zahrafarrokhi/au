from .models import User, OTP
from rest_framework import serializers
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'type', 'first_name',
                  'last_name', 'password', 'confirm_password']
        read_only_fields = ['id', 'phone_number', 'type']

    def validate(self, attrs):
        if attrs['confirm_password'] != attrs['passwrod']:
            raise serializers.ValidationError("Passwords dont mathch")
        return attrs


class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)

    def validate(self, attrs):
        user, created = User.objects.get_or_create(
            phone_number=attrs['phone_number'])
        exp_otp = OTP.objects.filter(user=user, is_active=True)
        for otp in exp_otp:
            otp.is_active = False
        OTP.objects.bulk_update(exp_otp, ['is_active'])
        attrs['user'] = user
        return attrs


class ValidateOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    value = serializers.CharField(max_length=5)

    def validate(self, attrs):
        phoneNumber = attrs['phone_number']
        token = attrs['value']
        try:
            user = User.objects.get(phone_number=phoneNumber)
            otp = OTP.objects.filter(
                user=user, value=token, is_active=True, exp_date__gte=timezone.now()).first()
            if otp is None:
                raise serializers.ValidationError('invalid otp')

            otp.is_active = False
            otp.save()

            attrs['user'] = user

        except User.DoesNotExist:
            raise serializers.ValidationError('user doesnt exist')
        except OTP.DoesNotExist:
            raise serializers.ValidationError('invalid otp')
        return attrs
