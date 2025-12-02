# assets/views.py
from rest_framework import viewsets, permissions, filters
from .models import Asset
from .serializers import AssetSerializer
from categories.models import Category

class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        return user.is_admin() or user.is_asset_manager()

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related('category').all()
    serializer_class = AssetSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name','serial_number','brand','category__name']
    ordering_fields = ['purchase_date','status','name']

    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            permission_classes = [IsAdminOrManager]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]

    def get_serializer(self, *args, **kwargs):
        ser = super().get_serializer(*args, **kwargs)
        # allow category PK assignment
        ser.fields['category'].queryset = Category.objects.all()
        return ser
