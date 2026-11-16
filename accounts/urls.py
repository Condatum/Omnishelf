from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('export/', views.export_library_view, name='export_library'),
    path('import/', views.import_library_view, name='import_library'),
]
