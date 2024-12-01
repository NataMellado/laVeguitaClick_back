from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    ROLES = [
        ('user', 'Usuario'),
        ('gerente', 'Gerente'),
        ('conductor', 'Conductor'),
    ]
    readonly_fields = ('id',)
    rol = models.CharField(max_length=20, choices=ROLES, default='user')
    email = models.EmailField(unique=True)
    username = None
    first_name = models.CharField(max_length=100, verbose_name='Nombre')
    last_name = models.CharField(max_length=100, verbose_name='Apellido')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email