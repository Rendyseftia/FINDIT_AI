from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    nama_lengkap = models.CharField(
        max_length=100
    )

    no_whatsapp = models.CharField(
        max_length=20,
        unique=True
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user'
    )

    #
    # OTP RESET PASSWORD
    #

    otp_code = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    otp_expired = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):

        return self.username