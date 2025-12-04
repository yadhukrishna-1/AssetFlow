from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import User
from assets.models import Asset
from assignments.models import Assignment
from categories.models import Category
from assets.forms import AssetForm
from assignments.forms import AssignmentForm
from .forms import CustomUserCreationForm
from django.db.models import Q, Count

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
    
    # Dashboard statistics
    total_assets = Asset.objects.count()
    available_assets = Asset.objects.filter(status='available').count()
    assigned_assets = Asset.objects.filter(status='assigned').count()
    total_users = User.objects.count()
    active_assignments = Assignment.objects.filter(active=True).count()
    
    # User statistics by role
    admin_count = User.objects.filter(role='admin').count()
    manager_count = User.objects.filter(role='asset_manager').count()
    employee_count = User.objects.filter(role='employee').count()
    
    context = {
        'total_assets': total_assets,
        'available_assets': available_assets,
        'assigned_assets': assigned_assets,
        'total_users': total_users,
        'active_assignments': active_assignments,
        'admin_count': admin_count,
        'manager_count': manager_count,
        'employee_count': employee_count,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required(login_url='login')
def asset_manager_dashboard(request):
    """Asset Manager dashboard - only for asset managers"""
    if not request.user.is_asset_manager():
        messages.error(request, 'Access denied. Asset Manager access required.')
        return redirect('home')
    
    # Dashboard statistics for asset managers
    total_assets = Asset.objects.count()
    available_assets = Asset.objects.filter(status='available').count()
    assigned_assets = Asset.objects.filter(status='assigned').count()
    repair_assets = Asset.objects.filter(status='under_repair').count()
    my_assignments = Assignment.objects.filter(assigned_by=request.user, active=True).count()
    
    context = {
        'total_assets': total_assets,
        'available_assets': available_assets,
        'assigned_assets': assigned_assets,
        'repair_assets': repair_assets,
        'my_assignments': my_assignments,
    }
    return render(request, 'asset_manager_dashboard.html', context)

@login_required(login_url='login')
def employee_dashboard(request):
    """Employee dashboard - for regular employees"""
    # Get employee's assignments
    my_assignments = Assignment.objects.filter(employee=request.user, active=True)
    assignment_history = Assignment.objects.filter(employee=request.user, active=False)[:5]
    
    context = {
        'my_assignments': my_assignments,
        'assignment_history': assignment_history,
        'total_assigned': my_assignments.count(),
    }
    return render(request, 'employee_dashboard.html', context)

# Admin-specific views
@login_required(login_url='login')
def manage_users(request):
    """Admin view to manage users"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    search_query = request.GET.get('search', '')
    users = User.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/manage_users.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required(login_url='login')
def create_user(request):
    """Admin view to create new user"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('manage_users')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'admin/create_user.html', {'form': form})

@login_required(login_url='login')
def bulk_create_users(request):
    """Admin view to create multiple users at once"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        users_data = request.POST.get('users_data', '').strip()
        if not users_data:
            messages.error(request, 'Please provide user data.')
            return render(request, 'admin/bulk_create_users.html')
        
        created_users = []
        errors = []
        
        for line_num, line in enumerate(users_data.split('\n'), 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                parts = [part.strip() for part in line.split(',')]
                if len(parts) < 5:
                    errors.append(f'Line {line_num}: Invalid format. Expected: username,email,first_name,last_name,role')
                    continue
                
                username, email, first_name, last_name, role = parts[:5]
                
                # Validate role
                valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
                if role not in valid_roles:
                    errors.append(f'Line {line_num}: Invalid role "{role}". Valid roles: {valid_roles}')
                    continue
                
                # Check admin restriction
                if role == 'admin' and User.objects.filter(role='admin').exists():
                    errors.append(f'Line {line_num}: Cannot create admin user. Only one admin is allowed.')
                    continue
                
                # Check if username already exists
                if User.objects.filter(username=username).exists():
                    errors.append(f'Line {line_num}: Username "{username}" already exists.')
                    continue
                
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password='password123',  # Default password
                    role=role
                )
                created_users.append(user)
                
            except Exception as e:
                errors.append(f'Line {line_num}: Error creating user - {str(e)}')
        
        if created_users:
            messages.success(request, f'Successfully created {len(created_users)} users.')
        if errors:
            for error in errors:
                messages.error(request, error)
        
        if created_users and not errors:
            return redirect('manage_users')
    
    return render(request, 'admin/bulk_create_users.html')

@login_required(login_url='login')
def edit_user(request, user_id):
    """Admin view to edit user"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Simple form handling for user editing
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        new_role = request.POST.get('role')
        
        # Prevent changing to admin if one already exists
        if new_role == 'admin' and user.role != 'admin':
            if User.objects.filter(role='admin').exists():
                messages.error(request, 'Only one admin user is allowed.')
                return render(request, 'admin/edit_user.html', {'user_obj': user})
        
        user.role = new_role
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        
        messages.success(request, 'User updated successfully!')
        return redirect('manage_users')
    
    return render(request, 'admin/edit_user.html', {'user_obj': user})

@login_required(login_url='login')
def manage_assets(request):
    """Admin view to manage assets"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    assets = Asset.objects.select_related('category').all()
    
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(brand__icontains=search_query)
        )
    
    if status_filter:
        assets = assets.filter(status=status_filter)
    
    paginator = Paginator(assets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/manage_assets.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Asset.STATUS_CHOICES
    })

@login_required(login_url='login')
def add_asset(request):
    """Add new asset"""
    if not (request.user.is_admin() or request.user.is_asset_manager()):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AssetForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset added successfully!')
            return redirect('manage_assets')
    else:
        form = AssetForm()
    
    return render(request, 'admin/add_asset.html', {'form': form})

@login_required(login_url='login')
def edit_asset(request, asset_id):
    """Edit existing asset"""
    if not (request.user.is_admin() or request.user.is_asset_manager()):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    asset = get_object_or_404(Asset, id=asset_id)
    
    if request.method == 'POST':
        form = AssetForm(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset updated successfully!')
            return redirect('manage_assets')
    else:
        form = AssetForm(instance=asset)
    
    return render(request, 'admin/edit_asset.html', {'form': form, 'asset': asset})

@login_required(login_url='login')
def delete_asset(request, asset_id):
    """Delete asset"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    asset = get_object_or_404(Asset, id=asset_id)
    
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Asset deleted successfully!')
        return redirect('manage_assets')
    
    return render(request, 'admin/delete_asset.html', {'asset': asset})

@login_required(login_url='login')
def manage_assignments(request):
    """Manage asset assignments"""
    if not (request.user.is_admin() or request.user.is_asset_manager()):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    assignments = Assignment.objects.select_related('asset', 'employee', 'assigned_by').filter(active=True)
    
    return render(request, 'admin/manage_assignments.html', {
        'assignments': assignments
    })

@login_required(login_url='login')
def create_assignment(request):
    """Create new assignment"""
    if not (request.user.is_admin() or request.user.is_asset_manager()):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.assigned_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('manage_assignments')
    else:
        form = AssignmentForm()
    
    return render(request, 'admin/create_assignment.html', {'form': form})

@login_required(login_url='login')
def return_asset(request, assignment_id):
    """Return an assigned asset"""
    if not (request.user.is_admin() or request.user.is_asset_manager()):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    assignment = get_object_or_404(Assignment, id=assignment_id, active=True)
    
    if request.method == 'POST':
        assignment.mark_returned()
        messages.success(request, f'Asset {assignment.asset.name} returned successfully!')
        if request.user.is_asset_manager():
            return redirect('asset_manager_assignments')
        return redirect('manage_assignments')
    
    template = 'asset_manager/return_asset.html' if request.user.is_asset_manager() else 'admin/return_asset.html'
    return render(request, template, {'assignment': assignment})

# Asset Manager specific views
@login_required(login_url='login')
def asset_manager_assets(request):
    """Asset Manager view to manage assets"""
    if not request.user.is_asset_manager():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    assets = Asset.objects.select_related('category').all()
    
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(brand__icontains=search_query)
        )
    
    if status_filter:
        assets = assets.filter(status=status_filter)
    
    paginator = Paginator(assets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'asset_manager/manage_assets.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Asset.STATUS_CHOICES
    })

@login_required(login_url='login')
def asset_manager_assignments(request):
    """Asset Manager view to manage assignments"""
    if not request.user.is_asset_manager():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    assignments = Assignment.objects.select_related('asset', 'employee', 'assigned_by').filter(active=True)
    
    return render(request, 'asset_manager/manage_assignments.html', {
        'assignments': assignments
    })

@login_required(login_url='login')
def asset_manager_users(request):
    """Asset Manager view to manage employees"""
    if not request.user.is_asset_manager():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    search_query = request.GET.get('search', '')
    users = User.objects.filter(role='employee')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'asset_manager/manage_users.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required(login_url='login')
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    if not request.user.is_asset_manager():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id, role='employee')
    user.is_active = not user.is_active
    user.save()
    
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('asset_manager_users')

@login_required(login_url='login')
def asset_manager_add_asset(request):
    """Asset Manager add new asset"""
    if not request.user.is_asset_manager():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AssetForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset added successfully!')
            return redirect('asset_manager_assets')
    else:
        form = AssetForm()
    
    return render(request, 'asset_manager/add_asset.html', {'form': form})

@login_required(login_url='login')
def asset_manager_edit_asset(request, asset_id):
    """Asset Manager edit asset"""
    if not request.user.is_asset_manager():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    asset = get_object_or_404(Asset, id=asset_id)
    
    if request.method == 'POST':
        form = AssetForm(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset updated successfully!')
            return redirect('asset_manager_assets')
    else:
        form = AssetForm(instance=asset)
    
    return render(request, 'asset_manager/edit_asset.html', {'form': form, 'asset': asset})

@login_required(login_url='login')
def asset_manager_create_assignment(request):
    """Asset Manager create assignment"""
    if not request.user.is_asset_manager():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.assigned_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('asset_manager_assignments')
    else:
        form = AssignmentForm()
    
    return render(request, 'asset_manager/create_assignment.html', {'form': form})

@login_required(login_url='login')
def delete_user(request, user_id):
    """Admin view to delete user"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deleting admin user
    if user.role == 'admin':
        messages.error(request, 'Cannot delete admin user.')
        return redirect('manage_users')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('manage_users')
    
    return render(request, 'admin/delete_user.html', {'user_obj': user})
