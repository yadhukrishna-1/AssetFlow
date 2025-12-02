# assets/serializers.py
from rest_framework import serializers
from .models import Asset
from categories.models import Category

class AssetSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

    class Meta:
        model = Asset
        fields = [
            'id',
            'name',
            'category',
            'brand',
            'serial_number',
            'purchase_date',
            'cost',
            'warranty_expiry',
            'status',
            'image',
            'description',
            'created_at',
            'updated_at',
        ]
