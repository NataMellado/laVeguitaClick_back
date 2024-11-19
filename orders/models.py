from django.db import models
from django.conf import settings
from products.models import Product

class Driver(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    license_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.license_number})"


class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('Moto', 'Moto'),
        ('Camioneta', 'Camioneta'),
        ('Bicicleta', 'Bicicleta'),
    ]

    license_plate = models.CharField(max_length=10, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    driver = models.OneToOneField(Driver, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle_type} - {self.license_plate} ({self.driver})"


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Enviado', 'Enviado'),
        ('Entregado', 'Entregado'),
        ('Cancelado', 'Cancelado'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pendiente')
    total_price = models.IntegerField(default=0) 
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_price(self):
        total = sum(item.get_total_price() for item in self.items.all())
        self.total_price = total
        return total

    def save(self, *args, **kwargs):
        """Guarda la orden sin volver a calcular el precio automáticamente."""
        if self.pk:
            self.calculate_total_price()
        super().save(*args, **kwargs)

    def __str__(self):
        vehicle_str = self.vehicle if self.vehicle else "No vehicle"
        return f"Order #{self.id} - {self.status} - Vehicle: {vehicle_str}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.IntegerField()

    def get_total_price(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        if not self.price:  
            self.price = self.product.price
        super().save(*args, **kwargs)  
        self.order.calculate_total_price() 
        self.order.save() 
