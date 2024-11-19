from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    ROLES = [
        ('user', 'Usuario'),
        ('gerente', 'Gerente'),
        ('conductor', 'Conductor'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='user')
    usuario = models.CharField(max_length=40, null=False, blank=False, default='Usuario')
    email = models.EmailField(unique=True)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email