#!/usr/bin/env python
"""
Emergency fix for Render deployment issues
This script will help diagnose and fix common deployment problems
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def check_environment():
    """Check deployment environment variables"""
    print("🔍 Checking deployment environment...")
    
    # Check if we're on Render
    render_env = os.getenv('RENDER', 'false')
    print(f"RENDER environment: {render_env}")
    
    # Check database URL
    database_url = os.getenv('DATABASE_URL', '')
    print(f"DATABASE_URL set: {'Yes' if database_url else 'No'}")
    if database_url:
        print(f"DATABASE_URL type: {database_url.split('://')[0] if '://' in database_url else 'Unknown'}")
    
    # Check other critical environment variables
    critical_vars = ['DEBUG', 'SECRET_KEY', 'ALLOWED_HOSTS']
    for var in critical_vars:
        value = os.getenv(var, 'Not set')
        print(f"{var}: {value}")
    
    return render_env == 'true', bool(database_url)

def check_database_connection():
    """Test database connection"""
    print("\n🔗 Testing database connection...")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_migrations():
    """Check if migrations are applied"""
    print("\n🔄 Checking database migrations...")
    
    try:
        from django.core.management import call_command
        from django.db.migrations.executor import MigrationExecutor
        from django.db.connection import connection
        
        executor = MigrationExecutor(connection)
        migrations = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if migrations:
            print(f"❌ Pending migrations: {len(migrations)}")
            for migration in migrations:
                print(f"   - {migration[0]}.{migration[1]}")
            return False
        else:
            print("✅ All migrations applied")
            return True
    except Exception as e:
        print(f"❌ Migration check failed: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    print("\n🔄 Running database migrations...")
    
    try:
        from django.core.management import call_command
        call_command('migrate', verbosity=2, interactive=False)
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def check_static_files():
    """Check static files collection"""
    print("\n📦 Checking static files...")
    
    try:
        from django.contrib.staticfiles.finders import get_finders
        from django.contrib.staticfiles.storage import staticfiles_storage
        
        # Test if static files storage is configured
        if hasattr(staticfiles_storage, 'exists'):
            print("✅ Static files storage configured")
            return True
        else:
            print("❌ Static files storage not properly configured")
            return False
    except Exception as e:
        print(f"❌ Static files check failed: {e}")
        return False

def collect_static_files():
    """Collect static files"""
    print("\n📦 Collecting static files...")
    
    try:
        from django.core.management import call_command
        call_command('collectstatic', verbosity=2, interactive=False)
        print("✅ Static files collected successfully")
        return True
    except Exception as e:
        print(f"❌ Static files collection failed: {e}")
        return False

def initialize_data():
    """Initialize initial data"""
    print("\n🔧 Initializing initial data...")
    
    try:
        from django.core.management import call_command
        
        # Try to run init_blood_stocks
        try:
            call_command('init_blood_stocks', verbosity=1)
            print("✅ Blood stocks initialized")
        except:
            print("ℹ️ Blood stocks already initialized or command not available")
        
        # Try to run setup_initial_data
        try:
            call_command('setup_initial_data', verbosity=1)
            print("✅ Initial data set up")
        except:
            print("ℹ️ Initial data already set up or command not available")
        
        return True
    except Exception as e:
        print(f"❌ Data initialization failed: {e}")
        return False

def main():
    """Main diagnostic and fix function"""
    print("🚀 BloodLink Emergency Fix and Diagnostics")
    print("=" * 50)
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
    django.setup()
    
    # Check environment
    is_render, has_db_url = check_environment()
    
    # Check database connection
    db_connected = check_database_connection()
    
    if not db_connected:
        print("\n🔧 Attempting to fix database connection...")
        # Try to run migrations
        if run_migrations():
            db_connected = check_database_connection()
    
    # Check migrations
    migrations_ok = check_migrations()
    if not migrations_ok:
        print("\n🔧 Running migrations...")
        run_migrations()
    
    # Check static files
    static_ok = check_static_files()
    if not static_ok:
        print("\n🔧 Collecting static files...")
        collect_static_files()
    
    # Initialize data
    initialize_data()
    
    # Final check
    print("\n" + "=" * 50)
    print("🎯 Final Status Check:")
    
    db_connected = check_database_connection()
    migrations_ok = check_migrations()
    static_ok = check_static_files()
    
    if db_connected and migrations_ok and static_ok:
        print("✅ All systems operational!")
        print("🎉 BloodLink should be working now!")
        return True
    else:
        print("❌ Some issues still exist:")
        if not db_connected:
            print("   - Database connection issues")
        if not migrations_ok:
            print("   - Migration issues")
        if not static_ok:
            print("   - Static files issues")
        return False

if __name__ == '__main__':
    main()
