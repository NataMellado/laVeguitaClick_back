from django.urls import path
from .views import login_view, logout_view

urlpatterns = [
    path('cuenta/login/', login_view, name='login'),
    path('cuenta/logout/', logout_view, name='logout'),
]