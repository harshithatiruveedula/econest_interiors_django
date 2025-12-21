from django.contrib import admin
from django.urls import path
import views   # import views from current folder

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/chat/', views.chat_api, name='chat_api'),
]
