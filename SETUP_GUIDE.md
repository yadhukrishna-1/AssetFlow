# AssetFlow Setup Guide

## Quick Start

### 1. Database Setup
```bash
cd project
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Sample Data (Optional)
```bash
python create_sample_data.py
```

### 3. Create Superuser (if not using sample data)
```bash
python manage.py createsuperuser
```

### 4. Run the Development Server
```bash
python manage.py runserver
```

### 5. Access the Application
- Open your browser and go to: `http://127.0.0.1:8000`
- You'll be redirected to the login page

## Sample Login Credentials (if using sample data)

### Admin Access
- **Username:** `admin`
- **Password:** `password123`
- **Capabilities:** Full system access, user management, all reports

### Asset Manager Access
- **Username:** `asset_manager`
- **Password:** `password123`
- **Capabilities:** Asset management, assignments, operational reports

### Employee Access
- **Username:** `john_doe` or `jane_smith`
- **Password:** `password123`
- **Capabilities:** View assigned assets, assignment history

## System Navigation

### Admin Dashboard
- **Manage Users:** View and manage all user accounts
- **Manage Assets:** Full asset CRUD operations
- **Manage Assignments:** Oversee all asset assignments
- **Asset Reports:** Generate and export system reports

### Asset Manager Dashboard
- **Manage Assets:** Add, edit, and track assets
- **Asset Assignments:** Create and manage assignments
- **Add New Asset:** Quick asset creation

### Employee Dashboard
- **My Assets:** View currently assigned assets
- **Asset History:** View past assignments

## Key Features

### Asset Management
- Add assets with images, categories, and detailed information
- Track asset status (Available, Assigned, Under Repair)
- Warranty and purchase date tracking
- Serial number management

### Assignment System
- Assign assets to employees
- Track assignment duration and expected returns
- Return processing with status updates
- Assignment history and audit trail

### Reporting
- Asset statistics and status reports
- Assignment tracking and analytics
- CSV export functionality
- Category-based asset distribution

### User Management
- Role-based access control (Admin, Asset Manager, Employee)
- User creation and role assignment
- Activity tracking and permissions

## File Structure
```
project/
├── accounts/          # User management and authentication
├── assets/           # Asset models, views, and forms
├── assignments/      # Assignment tracking system
├── categories/       # Asset categorization
├── reports/          # Reporting and analytics
├── templates/        # HTML templates
│   ├── admin/       # Admin-specific templates
│   └── reports/     # Report templates
├── media/           # Uploaded asset images
└── manage.py        # Django management script
```

## Troubleshooting

### Common Issues
1. **Migration errors:** Run `python manage.py makemigrations` then `python manage.py migrate`
2. **Permission denied:** Ensure you're logged in with appropriate role
3. **Missing images:** Check MEDIA_URL and MEDIA_ROOT settings
4. **Sample data errors:** Ensure migrations are applied before running sample data script

### Development Tips
- Use Django admin interface at `/admin/` for direct database access
- Check Django logs for detailed error information
- Ensure all required packages are installed in your virtual environment

## Production Deployment Notes
- Change DEBUG to False in settings.py
- Configure proper database (PostgreSQL recommended)
- Set up static file serving
- Configure email settings for notifications
- Implement proper backup procedures
- Set strong SECRET_KEY and secure passwords