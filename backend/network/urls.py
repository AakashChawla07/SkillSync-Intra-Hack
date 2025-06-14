from django.urls import path
from . import views

urlpatterns = [
    path('', views.network_dashboard, name='network_dashboard'),
    path('find-peers/', views.find_peers, name='find_peers'),
    path('buddy-request/<int:user_id>/', views.send_buddy_request, name='send_buddy_request'),
    path('network/respond-request/<int:request_id>/<str:action>/', views.respond_request, name='respond_request'),
]
