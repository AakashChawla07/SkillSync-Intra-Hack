from django.urls import path
from . import views

urlpatterns = [
    path('', views.domain_list, name='domain_list'),
    path('<int:domain_id>/', views.domain_detail, name='domain_detail'),
    path('<int:domain_id>/join/', views.join_domain, name='join_domain'),
]