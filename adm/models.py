from django.db import models
from django.contrib.auth.models import AbstractUser

class MyUser(AbstractUser):
    user_type = models.IntegerField(blank=False, null=False)
    REQUIRED_FIELDS = ['user_type']
