#!/usr/bin/env python
"""
Sample data creation script for AssetFlow
Run this script to populate the database with sample data for testing
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from accounts.models import User
from categories.models import Category
from assets.models import Asset
from assignments.models import Assignment

def create_sample_data():
    print("Creating sample data for AssetFlow...")
    
    # Create categories
    categories = [
        {'name': 'Laptops', 'description': 'Portable computers for employees'},
        {'name': 'Monitors', 'description': 'Display screens and monitors'},
        {'name': 'Mobile Phones', 'description': 'Company mobile devices'},
        {'name': 'Office Equipment', 'description': 'Printers, scanners, and other office equipment'},
        {'name': 'Furniture', 'description': 'Office furniture and fixtures'},
    ]
    
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"Created category: {category.name}")
    
    # Create users with admin restriction
    users_data = [
        {'username': 'admin', 'email': 'admin@company.com', 'first_name': 'System', 'last_name': 'Administrator', 'role': 'admin'},
        {'username': 'asset_manager', 'email': 'manager@company.com', 'first_name': 'Asset', 'last_name': 'Manager', 'role': 'asset_manager'},
        {'username': 'manager2', 'email': 'manager2@company.com', 'first_name': 'Sarah', 'last_name': 'Johnson', 'role': 'asset_manager'},
        {'username': 'john_doe', 'email': 'john@company.com', 'first_name': 'John', 'last_name': 'Doe', 'role': 'employee'},
        {'username': 'jane_smith', 'email': 'jane@company.com', 'first_name': 'Jane', 'last_name': 'Smith', 'role': 'employee'},
        {'username': 'bob_wilson', 'email': 'bob@company.com', 'first_name': 'Bob', 'last_name': 'Wilson', 'role': 'employee'},
        {'username': 'alice_brown', 'email': 'alice@company.com', 'first_name': 'Alice', 'last_name': 'Brown', 'role': 'employee'},
    ]
    
    for user_data in users_data:
        # Skip admin creation if one already exists
        if user_data['role'] == 'admin' and User.objects.filter(role='admin').exists():
            print(f"Admin user already exists, skipping {user_data['username']}")
            continue
            
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
            }
        )
        if created:
            user.set_password('password123')  # Default password for all users
            user.save()
            print(f"Created user: {user.username} ({user.get_role_display()})")
        else:
            print(f"User already exists: {user.username}")
    
    # Create assets
    laptop_category = Category.objects.get(name='Laptops')
    monitor_category = Category.objects.get(name='Monitors')
    phone_category = Category.objects.get(name='Mobile Phones')
    equipment_category = Category.objects.get(name='Office Equipment')
    
    assets_data = [
        {'name': 'Dell Latitude 7420', 'category': laptop_category, 'brand': 'Dell', 'serial_number': 'DL7420001', 'cost': 1299.99, 'status': 'available'},
        {'name': 'MacBook Pro 13"', 'category': laptop_category, 'brand': 'Apple', 'serial_number': 'MBP13001', 'cost': 1999.99, 'status': 'assigned'},
        {'name': 'ThinkPad X1 Carbon', 'category': laptop_category, 'brand': 'Lenovo', 'serial_number': 'TPX1C001', 'cost': 1599.99, 'status': 'available'},
        {'name': 'Dell UltraSharp 27"', 'category': monitor_category, 'brand': 'Dell', 'serial_number': 'DUS27001', 'cost': 399.99, 'status': 'assigned'},
        {'name': 'LG 24" Monitor', 'category': monitor_category, 'brand': 'LG', 'serial_number': 'LG24001', 'cost': 199.99, 'status': 'available'},
        {'name': 'iPhone 13 Pro', 'category': phone_category, 'brand': 'Apple', 'serial_number': 'IP13P001', 'cost': 999.99, 'status': 'assigned'},
        {'name': 'Samsung Galaxy S22', 'category': phone_category, 'brand': 'Samsung', 'serial_number': 'SGS22001', 'cost': 799.99, 'status': 'available'},
        {'name': 'HP LaserJet Pro', 'category': equipment_category, 'brand': 'HP', 'serial_number': 'HPLJ001', 'cost': 299.99, 'status': 'under_repair'},
    ]
    
    for asset_data in assets_data:
        asset, created = Asset.objects.get_or_create(
            serial_number=asset_data['serial_number'],
            defaults={
                'name': asset_data['name'],
                'category': asset_data['category'],
                'brand': asset_data['brand'],
                'cost': asset_data['cost'],
                'status': asset_data['status'],
                'purchase_date': date.today() - timedelta(days=30),
                'warranty_expiry': date.today() + timedelta(days=365),
                'description': f"Sample {asset_data['name']} for testing purposes"
            }
        )
        if created:
            print(f"Created asset: {asset.name} ({asset.serial_number})")
    
    # Create some assignments
    asset_manager = User.objects.get(username='asset_manager')
    john = User.objects.get(username='john_doe')
    jane = User.objects.get(username='jane_smith')
    
    # Assign MacBook to John
    macbook = Asset.objects.get(serial_number='MBP13001')
    assignment1, created = Assignment.objects.get_or_create(
        asset=macbook,
        employee=john,
        defaults={
            'assigned_by': asset_manager,
            'expected_return_date': date.today() + timedelta(days=90),
            'remarks': 'For development work'
        }
    )
    if created:
        print(f"Created assignment: {macbook.name} -> {john.get_full_name()}")
    
    # Assign Monitor to Jane
    monitor = Asset.objects.get(serial_number='DUS27001')
    assignment2, created = Assignment.objects.get_or_create(
        asset=monitor,
        employee=jane,
        defaults={
            'assigned_by': asset_manager,
            'expected_return_date': date.today() + timedelta(days=180),
            'remarks': 'For design work'
        }
    )
    if created:
        print(f"Created assignment: {monitor.name} -> {jane.get_full_name()}")
    
    # Assign iPhone to John
    iphone = Asset.objects.get(serial_number='IP13P001')
    assignment3, created = Assignment.objects.get_or_create(
        asset=iphone,
        employee=john,
        defaults={
            'assigned_by': asset_manager,
            'remarks': 'Company phone for business use'
        }
    )
    if created:
        print(f"Created assignment: {iphone.name} -> {john.get_full_name()}")
    
    print("\nSample data creation completed!")
    print("\nLogin credentials (password: 'password123' for all):")
    print("Admin: username='admin'")
    print("Asset Managers: username='asset_manager', 'manager2'")
    print("Employees: username='john_doe', 'jane_smith', 'bob_wilson', 'alice_brown'")
    print("\nNote: You can create additional users through the admin panel or use:")
    print("python manage.py createusers --batch  # Create sample users")
    print("python manage.py createusers  # Create single user interactively")

if __name__ == '__main__':
    create_sample_data()