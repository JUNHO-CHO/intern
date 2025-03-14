from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = models.CharField(max_length=15, unique=True)
    nickname = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=10)
