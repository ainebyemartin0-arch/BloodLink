from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def home_redirect(request):
    return redirect('/donor/')

urlpatterns = [
    # Note: Django admin disabled due to Python 3.14 compatibility issues
    # path('admin/', admin.site.urls),
    path('', home_redirect),
    path('staff/', include('staff_portal.urls', namespace='staff')),
    path('donor/', include('donor_portal.urls', namespace='donor')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'bloodlink_project.views.error_404'
