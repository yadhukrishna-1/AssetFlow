from django.urls import path
from . import views

urlpatterns = [
    # Employee URLs
    path('', views.employee_requests, name='employee_requests'),
    path('new/', views.new_asset_request, name='new_asset_request'),
    path('return/', views.return_request, name='return_request'),
    
    # Manager URLs
    path('manager/', views.manager_requests, name='manager_requests'),
    path('manager/<int:request_id>/approve/', views.manager_approve_request, name='manager_approve_request'),
    
    # Admin URLs
    path('admin/', views.admin_requests, name='admin_requests'),
    path('admin/<int:request_id>/approve/', views.admin_approve_request, name='admin_approve_request'),
]