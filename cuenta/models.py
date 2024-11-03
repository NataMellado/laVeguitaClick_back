from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    ROLES = [
        ('user', 'Usuario'),
        ('gerente', 'Gerente'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='user')

    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True)
    # groups y user_permissions son campos que ya existen en AbstractUser}
    # pero los sobreescribimos para evitar un error al cambiar el modelo de autenticación
