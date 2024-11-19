# Generated by Django 5.1 on 2024-11-18 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_customuser_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='rol',
            field=models.CharField(choices=[('user', 'Usuario'), ('gerente', 'Gerente'), ('conductor', 'Conductor')], default='user', max_length=20),
        ),
    ]