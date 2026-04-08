from django.urls import path, include
from . import views
from . import api_views
from notifications.api_views import check_delivery_status

app_name = 'staff'

urlpatterns = [
    path('', views.redirect_root, name='root'),
    path('login/', views.staff_login, name='login'),
    path('logout/', views.staff_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register_staff, name='register'),
    path('donors/', views.donor_list, name='donor_list'),
    path('donors/add/', views.donor_add, name='donor_add'),
    path('donors/<int:pk>/', views.donor_detail, name='donor_detail'),
    path('donors/<int:pk>/edit/', views.donor_edit, name='donor_edit'),
    path('donors/<int:pk>/toggle/', views.donor_toggle_availability, name='donor_toggle'),
    path('donors/<int:pk>/delete/', views.donor_delete, name='donor_delete'),
    path('requests/', views.request_list, name='request_list'),
    path('requests/create/', views.request_create, name='request_create'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('requests/<int:pk>/close/', views.request_close, name='request_close'),
    path('requests/<int:pk>/delete/', views.request_delete, name='request_delete'),
    path('reports/', views.reports, name='reports'),
    
    # Donation management
    path('donations/', views.donation_list, name='donation_list'),
    path('donations/create/', views.donation_create, name='donation_create'),
    path('donations/<int:pk>/', views.donation_detail, name='donation_detail'),
    
    # API endpoints for blood shortage
    path('api/check-shortage/', views.check_shortage_api, name='api_check_shortage'),
    
    # API endpoints for notifications
    path('api/notifications/check/', api_views.check_notifications, name='api_check_notifications'),
    path('api/notifications/mark-read/', api_views.mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/clear-session/', api_views.clear_session_notification, name='api_clear_session_notification'),
    path('api/notifications/check-delivery-status/<int:notification_id>/', check_delivery_status, name='api_check_delivery_status'),
    path('api/stats/', api_views.get_system_stats, name='api_system_stats'),
    
    # Notifications management
    path('notifications/', include('notifications.urls')),
]
