from django.http import HttpResponse
from django.urls import path

app_name = 'accounts'

urlpatterns = [
    path('login/', lambda r: HttpResponse('Login placeholder'), name='login'),
    path('register/', lambda r: HttpResponse('Register placeholder'), name='register'),
    path('logout/', lambda r: HttpResponse('Logout placeholder'), name='logout'),
]
