# Evaluación Ingeniería de Software

- Cristobal Sanchez
- Natalia Mellado
- Pablo Bravo

> ** Install steps **
1. Clone the repository
2. Run `pip install -r requirements.txt`
3. Run `python manage.py migrate`
4. Run `python manage.py runserver`
5. Run `python manage.py loaddata initial_data.json`



# Crear usuarios:

1. python manage.py shell

2. Crea los usuarios con el método create_user (esto automáticamente genera las contraseñas correctamente hasheadas):
    ```from accounts.models import CustomUser
    user1 = CustomUser.objects.create_user(id=1, email="gerente@gmail.com", password="123", usuario="Gerente", rol="gerente")
    user2 = CustomUser.objects.create_user(id=2, email="usuario1@gmail.com", password="123", usuario="Usuario 1", rol="user")
    user3 = CustomUser.objects.create_user(id=3, email="usuario2@gmail.com", password="123", usuario="Usuario 2", rol="user")
    user4 = CustomUser.objects.create_user(id=4, email="conductor1@example.com", password="123", usuario="Driver 1", rol="conductor")
    user5 = CustomUser.objects.create_user(id=5, email="conductor2@example.com", password="123", usuario="Driver 2", rol="conductor")
    user6 = CustomUser.objects.create_user(id=6, email="conductor3@example.com", password="123", usuario="Driver 3", rol="conductor")```

    
3. Exporta los usuarios como fixtures: Usa el comando dumpdata para exportar los usuarios creados como un fixture JSON:
    `python manage.py dumpdata accounts.CustomUser --indent 2 > accounts/fixtures/initial_data.json`

4. Recarga el fixture si lo necesitas: Flushea la base de datos y recarga los datos desde el archivo generado:
    `python manage.py flush`
    `python manage.py loaddata accounts/fixtures/initial_data.json`


