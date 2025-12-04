# User Management in AssetFlow

AssetFlow now supports creating multiple users with different roles while maintaining the single admin restriction, similar to Django's admin system.

## User Roles

1. **Admin** (Only one allowed)
   - Full system access
   - Can create, edit, and delete users
   - Can manage all assets and assignments
   - Access to all reports and system settings

2. **Asset Manager** (Multiple allowed)
   - Can manage assets and assignments
   - Can view and manage employees
   - Can create assignments and return assets
   - Limited user management (employees only)

3. **Employee** (Multiple allowed)
   - Can view their assigned assets
   - Can see assignment history
   - Read-only access to their data

## Creating Users

### 1. Single User Creation (Web Interface)
- Navigate to Admin Dashboard → Manage Users → Create New User
- Fill in user details and select role
- Admin role will be disabled if one already exists

### 2. Bulk User Creation (Web Interface)
- Navigate to Admin Dashboard → Manage Users → Bulk Create Users
- Use CSV format: `username,email,first_name,last_name,role`
- Example:
  ```
  john_doe,john@company.com,John,Doe,employee
  jane_smith,jane@company.com,Jane,Smith,asset_manager
  ```

### 3. Management Command (Terminal)
```bash
# Create single user interactively
python manage.py createusers

# Create single user with parameters
python manage.py createusers --username john --email john@company.com --first-name John --last-name Doe --role employee --password mypassword

# Create sample users for testing
python manage.py createusers --batch
```

### 4. Sample Data Script
```bash
python create_sample_data.py
```

## Admin Restriction

- Only **one admin user** is allowed in the system
- If an admin already exists:
  - Admin role won't appear in user creation forms
  - Bulk creation will skip admin users
  - Management command will prevent admin creation
- Admin users cannot be deleted through the interface

## Default Passwords

- All users created through bulk creation or sample data use default passwords
- Users should change their password after first login
- Default passwords:
  - Sample data: `password123`
  - Management command batch: `admin123`, `manager123`, `employee123`

## User Statistics

The admin dashboard shows:
- Total users by role
- Active assignments
- Asset distribution
- System overview

## Security Notes

- Admin role is protected from deletion
- Role changes are validated to prevent multiple admins
- User creation requires admin privileges
- Default passwords should be changed immediately