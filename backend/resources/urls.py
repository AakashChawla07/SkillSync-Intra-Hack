from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_list, name='resource_list'),
    path('<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('upload/', views.upload_resource, name='upload_resource'),
    path('filter',views.filter_resources,name='filter_resources'),
]
