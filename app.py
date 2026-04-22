import os
import sys
from django.core.wsgi import get_wsgi_application

# Add to project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodlink_project.settings')

# Get Django WSGI application
application = get_wsgi_application()
