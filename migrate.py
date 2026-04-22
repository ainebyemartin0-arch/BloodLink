#!/usr/bin/env python
"""
Migration script for Render.com deployment
"""
import os
import django
from django.core.management import execute_from_command_line

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

def run_migrations():
    """Run all migrations and setup initial data"""
    print("Starting database migration process...")
    
    try:
        # Create migrations
        print("Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # Apply migrations
        print("Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Setup initial data
        print("Setting up initial data...")
        execute_from_command_line(['manage.py', 'setup_initial_data'])
        
        # Collect static files
        print("Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        print("Migration process completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        raise

if __name__ == '__main__':
    run_migrations()
