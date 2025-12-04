from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Count, Q
from assets.models import Asset
from assignments.models import Assignment
from accounts.models import User
import csv
from datetime import datetime, timedelta

@login_required(login_url='login')
def asset_report(request):
    """Generate asset report"""
    if not (request.user.is_admin() or request.user.is_asset_manager()):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Asset statistics
    total_assets = Asset.objects.count()
    available_assets = Asset.objects.filter(status='available').count()
    assigned_assets = Asset.objects.filter(status='assigned').count()
    repair_assets = Asset.objects.filter(status='under_repair').count()
    
    # Assets by category
    assets_by_category = Asset.objects.values('category__name').annotate(count=Count('id'))
    
    context = {
        'total_assets': total_assets,
        'available_assets': available_assets,
        'assigned_assets': assigned_assets,
        'repair_assets': repair_assets,
        'assets_by_category': assets_by_category,
    }
    
    return render(request, 'reports/asset_report.html', context)

@login_required(login_url='login')
def assignment_report(request):
    """Generate assignment report"""
    if not (request.user.is_admin() or request.user.is_asset_manager()):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Assignment statistics
    active_assignments = Assignment.objects.filter(active=True).count()
    total_assignments = Assignment.objects.count()
    returned_assignments = Assignment.objects.filter(active=False).count()
    
    # Recent assignments
    recent_assignments = Assignment.objects.select_related('asset', 'employee').order_by('-assigned_date')[:10]
    
    context = {
        'active_assignments': active_assignments,
        'total_assignments': total_assignments,
        'returned_assignments': returned_assignments,
        'recent_assignments': recent_assignments,
    }
    
    return render(request, 'reports/assignment_report.html', context)

@login_required(login_url='login')
def export_assets_csv(request):
    """Export assets to CSV with assignment details"""
    if not (request.user.is_admin() or request.user.is_asset_manager()):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="assets_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Serial Number', 'Category', 'Brand', 'Status', 'Purchase Date', 'Cost', 'Warranty Expiry', 'Assigned To', 'Assignment Date', 'Expected Return'])
    
    assets = Asset.objects.select_related('category').prefetch_related('assignments').all()
    for asset in assets:
        # Get current assignment if any
        current_assignment = asset.assignments.filter(active=True).first()
        
        assigned_to = ''
        assignment_date = ''
        expected_return = ''
        
        if current_assignment:
            assigned_to = current_assignment.employee.get_full_name() or current_assignment.employee.username
            assignment_date = current_assignment.assigned_date.strftime('%Y-%m-%d')
            expected_return = current_assignment.expected_return_date.strftime('%Y-%m-%d') if current_assignment.expected_return_date else ''
        
        writer.writerow([
            asset.name,
            asset.serial_number,
            asset.category.name,
            asset.brand or '',
            asset.get_status_display(),
            asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else '',
            asset.cost or '',
            asset.warranty_expiry.strftime('%Y-%m-%d') if asset.warranty_expiry else '',
            assigned_to,
            assignment_date,
            expected_return
        ])
    
    return response

@login_required(login_url='login')
def export_assignments_csv(request):
    """Export assignments to CSV"""
    if not (request.user.is_admin() or request.user.is_asset_manager()):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="assignments_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Asset Name', 'Serial Number', 'Employee', 'Assigned By', 'Assigned Date', 'Expected Return', 'Returned Date', 'Status', 'Remarks'])
    
    assignments = Assignment.objects.select_related('asset', 'employee', 'assigned_by').all()
    for assignment in assignments:
        writer.writerow([
            assignment.asset.name,
            assignment.asset.serial_number,
            assignment.employee.get_full_name() or assignment.employee.username,
            assignment.assigned_by.get_full_name() or assignment.assigned_by.username if assignment.assigned_by else '',
            assignment.assigned_date.strftime('%Y-%m-%d'),
            assignment.expected_return_date.strftime('%Y-%m-%d') if assignment.expected_return_date else '',
            assignment.returned_date.strftime('%Y-%m-%d') if assignment.returned_date else '',
            'Active' if assignment.active else 'Returned',
            assignment.remarks or ''
        ])
    
    return response
