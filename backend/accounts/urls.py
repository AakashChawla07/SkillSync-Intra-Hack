from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_home, name='dashboard'),
]
