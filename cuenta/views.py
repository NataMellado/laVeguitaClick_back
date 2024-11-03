from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username', None)
        password = data.get('password', None)

        usuario = authenticate(username=username, password=password)

        if usuario is not None:
            login(request, usuario)
            return JsonResponse({'message': 'Login exitoso!', 'rol': usuario.rol}, status=200)
        else:
            return JsonResponse({'error': 'Credenciales inválidas!'}, status=400)
    return JsonResponse({'error': 'Petición inválida!'}, status=400)


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout exitoso!'}, status=200)
    return JsonResponse({'error': 'Petición inválida!'}, status=400)
