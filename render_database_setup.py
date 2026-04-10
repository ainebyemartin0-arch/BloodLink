#!/usr/bin/env python
"""
Render Database Setup Script
Run this after deployment to set up the database
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')
django.setup()

from django.core.management import execute_from_command_line

def setup_database():
    """Run database migrations and create superuser"""
    print("Setting up BloodLink database...")
    
    # Run migrations
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    print("Migrations completed!")
    
    # You'll need to create a superuser manually in the Render shell
    print("Please create a superuser by running:")
    print("python manage.py createsuperuser")

if __name__ == '__main__':
    setup_database()
