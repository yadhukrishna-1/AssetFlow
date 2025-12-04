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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)