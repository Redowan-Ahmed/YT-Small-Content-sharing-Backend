from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserProfileManager

class UserProfile(AbstractUser):
    username = None
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    phone_number = models.CharField(max_length=16, blank=True, db_index=True)
    is_online = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False, blank=True)
    otp = models.CharField(max_length=10, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserProfileManager()

    def __str__(self):
        return self.email