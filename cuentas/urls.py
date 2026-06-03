from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import LoginView

app_name = 'cuentas'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]