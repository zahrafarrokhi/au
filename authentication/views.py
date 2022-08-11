from django.shortcuts import render
from .models import OTP, User
from . import serializers
from rest_framework import generics, status, viewsets, mixins
from datetime import timedelta, datetime
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.


class SendOtp(APIView):
    serializer_class = serializers.PhoneSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = serializer.validated_data['user']
            otp = OTP.objects.create(user=user, type=OTP.SMS, is_active=True,
                                     exp_date=(timezone.now() +
                                               timedelta(minutes=2)))
            return Response({'message': 'an otp has been sent'}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class LoginOtp(APIView):
    serializer_class = serializers.ValidateOtpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)


class LoginPass(APIView):

    def post(self, request, *args, **kwargs):
        user = authenticate(
            username=request.data['phone_number'], password=request.data['password'])
        if user is not None:
            login(request, user)

        else:
            return Response({'error': 'invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)


class ForgetPass(APIView):

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user is not None:
            user.set_password(self.request.data['password'])
            user.save()
        return Response(status=status.HTTP_200_OK)


class SignUp(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user
