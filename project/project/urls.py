"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# corporate_asset_mgmt/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from rest_framework import routers
from assets.views import AssetViewSet
from assignments.views import AssignmentViewSet
from accounts import views as accounts_views
from reports import views as reports_views

router = routers.DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'assignments', AssignmentViewSet, basename='assignment')

def home_redirect(request):
    """Redirect to appropriate dashboard based on user role or to login"""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_admin():
        return redirect('admin_dashboard')
    elif request.user.is_asset_manager():
        return redirect('asset_manager_dashboard')
    else:
        return redirect('employee_dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('', home_redirect, name='home'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', accounts_views.custom_login, name='login'),
    path('logout/', accounts_views.custom_logout, name='logout'),
    path('admin-dashboard/', accounts_views.admin_dashboard, name='admin_dashboard'),
    path('asset-manager-dashboard/', accounts_views.asset_manager_dashboard, name='asset_manager_dashboard'),
    path('employee-dashboard/', accounts_views.employee_dashboard, name='employee_dashboard'),
    
    # Admin management URLs
    path('admin-panel/users/', accounts_views.manage_users, name='manage_users'),
    path('admin-panel/users/create/', accounts_views.create_user, name='create_user'),
    path('admin-panel/users/bulk-create/', accounts_views.bulk_create_users, name='bulk_create_users'),
    path('admin-panel/users/<int:user_id>/edit/', accounts_views.edit_user, name='edit_user'),
    path('admin-panel/users/<int:user_id>/delete/', accounts_views.delete_user, name='delete_user'),
    path('admin-panel/assets/', accounts_views.manage_assets, name='manage_assets'),
    path('admin-panel/assets/add/', accounts_views.add_asset, name='add_asset'),
    path('admin-panel/assets/<int:asset_id>/edit/', accounts_views.edit_asset, name='edit_asset'),
    path('admin-panel/assets/<int:asset_id>/delete/', accounts_views.delete_asset, name='delete_asset'),
    path('admin-panel/assignments/', accounts_views.manage_assignments, name='manage_assignments'),
    path('admin-panel/assignments/create/', accounts_views.create_assignment, name='create_assignment'),
    path('admin-panel/assignments/<int:assignment_id>/return/', accounts_views.return_asset, name='return_asset'),
    
    # Asset Manager URLs
    path('asset-manager/assets/', accounts_views.asset_manager_assets, name='asset_manager_assets'),
    path('asset-manager/assignments/', accounts_views.asset_manager_assignments, name='asset_manager_assignments'),
    path('asset-manager/users/', accounts_views.asset_manager_users, name='asset_manager_users'),
    path('asset-manager/users/<int:user_id>/toggle/', accounts_views.toggle_user_status, name='toggle_user_status'),
    path('asset-manager/assets/add/', accounts_views.asset_manager_add_asset, name='asset_manager_add_asset'),
    path('asset-manager/assets/<int:asset_id>/edit/', accounts_views.asset_manager_edit_asset, name='asset_manager_edit_asset'),
    path('asset-manager/assignments/create/', accounts_views.asset_manager_create_assignment, name='asset_manager_create_assignment'),
    
    # Reports URLs
    path('reports/assets/', reports_views.asset_report, name='asset_report'),
    path('reports/assignments/', reports_views.assignment_report, name='assignment_report'),
    path('reports/export/assets/', reports_views.export_assets_csv, name='export_assets_csv'),
    path('reports/export/assignments/', reports_views.export_assignments_csv, name='export_assignments_csv'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)