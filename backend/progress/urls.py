from django.urls import path
from . import views

urlpatterns = [
    path('', views.progress_dashboard, name='progress_dashboard'),
    path('create-goal/', views.create_goal, name='create_goal'),
    path('goal/<int:goal_id>/', views.goal_detail, name='goal_detail'),
]
