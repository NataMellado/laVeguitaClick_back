from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        ...
    return JsonResponse({'error': 'Petición inválida!'}, status=400)

def logout_view(request):
    if request.method == 'POST':
        ...
    return JsonResponse({'error': 'Petición inválida!'}, status=400)