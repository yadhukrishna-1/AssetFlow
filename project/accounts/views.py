from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def custom_login(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def custom_logout(request):
    """Handle user logout"""
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def admin_dashboard(request):
    """Admin dashboard - only for admins"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admin access required.')
        return redirect('home')
    return render(request, 'admin_dashboard.html')

@login_required(login_url='login')
def asset_manager_dashboard(request):
    """Asset Manager dashboard - only for asset managers"""
    if not request.user.is_asset_manager():
        messages.error(request, 'Access denied. Asset Manager access required.')
        return redirect('home')
    return render(request, 'asset_manager_dashboard.html')

@login_required(login_url='login')
def employee_dashboard(request):
    """Employee dashboard - for regular employees"""
    return render(request, 'employee_dashboard.html')
