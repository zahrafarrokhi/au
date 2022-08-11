from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.crypto import get_random_string
import string
# Create your models here.

# Create your models here.


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, phone_number=None, email=None, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(
            email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number=None, email=None, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone_number, email, password , **extra_fields)


class User(AbstractUser):
    username = None

    ADMIN = 'admin'
    ASSISTANT = 'assistant'
    ATTENDEE = 'attendee'
    SUPPORT = 'support'
    USER_TYPE_CHOICES = (
        (ADMIN, 'Admin'),
        (ASSISTANT, 'Assistant'),
        (SUPPORT, 'Support'),
        (ATTENDEE, 'Attendee')
    )
    type = models.CharField(choices=USER_TYPE_CHOICES,
                            default=ATTENDEE, max_length=32)
    phone_number = models.CharField(max_length=11,
                                    unique=True, null=True, default=None)
    phone_number_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'

    objects = CustomUserManager()

    def __str__(self):
        username = self.phone_number
        return f"{username}"


def generate_numeric_token():
    return get_random_string(length=5, allowed_chars=string.digits)


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    EMAIL = 'email'
    SMS = 'sms'
    OTP_CHOICES = ((EMAIL, 'E-Mail'), (SMS, 'SMS'),)
    type = models.CharField(max_length=10, choices=OTP_CHOICES, default=SMS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    exp_date = models.DateTimeField(blank=False, null=False)
    is_active = models.BooleanField(default=True)
    value = models.CharField(default=generate_numeric_token, max_length=10)

    def __str__(self):
        return str(f"{self.value} sent by {str(self.type)} to "
                   f"{self.user.email if self.type == 'email' else self.user.phone_number}")
