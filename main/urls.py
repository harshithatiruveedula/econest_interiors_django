from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('setup/', views.setup_view, name='setup'),
    path('dashboard-access/', views.dashboard_access, name='dashboard_access'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/consultation/<int:id>/edit/', views.edit_consultation, name='edit_consultation'),
    path('dashboard/consultation/<int:id>/delete/', views.delete_consultation, name='delete_consultation'),
    path('api/chat/', views.chat_ai, name='chat_ai'),
]




