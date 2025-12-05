from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import AssetRequest
from .forms import NewAssetRequestForm, ReturnRequestForm
from assignments.models import Assignment

@login_required
def employee_requests(request):
    """Employee view to see their requests"""
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    requests = AssetRequest.objects.filter(employee=request.user).order_by('-created_at')
    return render(request, 'requests/employee_requests.html', {'requests': requests})

@login_required
def new_asset_request(request):
    """Employee creates new asset request"""
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = NewAssetRequestForm(request.POST)
        if form.is_valid():
            asset_request = form.save(commit=False)
            asset_request.employee = request.user
            asset_request.request_type = 'new'
            asset_request.save()
            messages.success(request, 'Asset request submitted successfully!')
            return redirect('employee_requests')
    else:
        form = NewAssetRequestForm()
    
    return render(request, 'requests/new_asset_request.html', {'form': form})

@login_required
def return_request(request):
    """Employee creates return request"""
    if not request.user.is_employee():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Check if asset is pre-selected from dashboard
    asset_id = request.GET.get('asset')
    initial_data = {}
    if asset_id:
        try:
            from assets.models import Asset
            asset = Asset.objects.get(id=asset_id, assignments__employee=request.user, assignments__active=True)
            initial_data['asset'] = asset
        except Asset.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = ReturnRequestForm(request.user, request.POST)
        if form.is_valid():
            asset_request = form.save(commit=False)
            asset_request.employee = request.user
            asset_request.request_type = 'return'
            asset_request.save()
            messages.success(request, 'Return request submitted successfully!')
            return redirect('employee_requests')
    else:
        form = ReturnRequestForm(request.user, initial=initial_data)
    
    return render(request, 'requests/return_request.html', {'form': form})

@login_required
def manager_requests(request):
    """Asset Manager view to approve/reject requests"""
    if not request.user.is_asset_manager():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    pending_requests = AssetRequest.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'requests/manager_requests.html', {'requests': pending_requests})

@login_required
def manager_approve_request(request, request_id):
    """Asset Manager approves request"""
    if not request.user.is_asset_manager():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    asset_request = get_object_or_404(AssetRequest, id=request_id, status='pending')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        if action == 'approve':
            # For new asset requests, manager must select specific asset
            if asset_request.request_type == 'new':
                selected_asset_id = request.POST.get('selected_asset')
                if selected_asset_id:
                    from assets.models import Asset
                    try:
                        selected_asset = Asset.objects.get(id=selected_asset_id, status=Asset.STATUS_AVAILABLE)
                        asset_request.requested_asset = selected_asset
                    except Asset.DoesNotExist:
                        messages.error(request, 'Selected asset is no longer available.')
                        return render(request, 'requests/manager_approve.html', {
                            'asset_request': asset_request,
                            'available_assets': Asset.objects.filter(category=asset_request.category, status=Asset.STATUS_AVAILABLE)
                        })
                else:
                    messages.error(request, 'Please select an asset to assign.')
                    return render(request, 'requests/manager_approve.html', {
                        'asset_request': asset_request,
                        'available_assets': Asset.objects.filter(category=asset_request.category, status=Asset.STATUS_AVAILABLE)
                    })
            
            asset_request.status = 'manager_approved'
            asset_request.manager_approved_by = request.user
            asset_request.manager_approved_at = timezone.now()
            asset_request.manager_comments = comments
            asset_request.save()
            messages.success(request, 'Request approved and sent to admin for final approval.')
        elif action == 'reject':
            asset_request.status = 'rejected'
            asset_request.manager_comments = comments
            asset_request.save()
            messages.success(request, 'Request rejected.')
        
        return redirect('manager_requests')
    
    # For GET requests, include available assets for new requests
    context = {'asset_request': asset_request}
    if asset_request.request_type == 'new':
        from assets.models import Asset
        context['available_assets'] = Asset.objects.filter(
            category=asset_request.category, 
            status=Asset.STATUS_AVAILABLE
        )
    
    return render(request, 'requests/manager_approve.html', context)

@login_required
def admin_requests(request):
    """Admin view to see manager-approved requests"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    approved_requests = AssetRequest.objects.filter(status='manager_approved').order_by('-created_at')
    return render(request, 'requests/admin_requests.html', {'requests': approved_requests})

@login_required
def admin_approve_request(request, request_id):
    """Admin final approval and completion"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    asset_request = get_object_or_404(AssetRequest, id=request_id, status='manager_approved')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        if action == 'approve':
            asset_request.status = 'admin_approved'
            asset_request.admin_approved_by = request.user
            asset_request.admin_approved_at = timezone.now()
            asset_request.admin_comments = comments
            
            # Handle new asset requests - create assignment
            if asset_request.request_type == 'new':
                from assets.models import Asset
                
                # Check if specific asset was requested
                if asset_request.requested_asset:
                    if asset_request.requested_asset.status == Asset.STATUS_AVAILABLE:
                        available_asset = asset_request.requested_asset
                    else:
                        available_asset = None
                        messages.warning(request, f'Requested asset {asset_request.requested_asset.name} is no longer available. Please assign manually.')
                else:
                    # Find any available asset in requested category
                    available_asset = Asset.objects.filter(
                        category=asset_request.category,
                        status=Asset.STATUS_AVAILABLE
                    ).first()
                
                if available_asset:
                    # Create assignment
                    Assignment.objects.create(
                        asset=available_asset,
                        employee=asset_request.employee,
                        assigned_by=request.user,
                        remarks=f'Assigned via request: {asset_request.description}'
                    )
                    asset_request.status = 'completed'
                    messages.success(request, f'Request approved and {available_asset.name} assigned to {asset_request.employee.get_full_name()}!')
                else:
                    messages.warning(request, 'Request approved but no available assets in this category. Please assign manually.')
            
            # Handle return requests - mark assignment as returned
            elif asset_request.request_type == 'return':
                assignment = Assignment.objects.filter(
                    asset=asset_request.asset, 
                    employee=asset_request.employee, 
                    active=True
                ).first()
                if assignment:
                    assignment.mark_returned()
                    asset_request.status = 'completed'
                    messages.success(request, f'Return approved and {asset_request.asset.name} returned to available pool.')
            
            asset_request.save()
        elif action == 'reject':
            asset_request.status = 'rejected'
            asset_request.admin_comments = comments
            asset_request.save()
            messages.success(request, 'Request rejected.')
        
        return redirect('admin_requests')
    
    return render(request, 'requests/admin_approve.html', {'asset_request': asset_request})