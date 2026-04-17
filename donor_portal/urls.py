from django.urls import path
from . import views
from . import api_views

app_name = 'donor'

urlpatterns = [
    path('', views.donor_home, name='home'),
    path('about/', views.about_bloodlink, name='about'),
    path('register/', views.donor_register, name='register'),
    path('login/', views.donor_login, name='login'),
    path('logout/', views.donor_logout, name='logout'),
    path('dashboard/', views.donor_dashboard, name='dashboard'),
    path('profile/', views.donor_profile, name='profile'),
    path('profile/edit/', views.donor_profile_edit, name='profile_edit'),
    path('donations/', views.donor_donations, name='donations'),
    path('requests/', views.donor_requests, name='donor_requests'),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('cancel-request/<int:pk>/', views.cancel_request, name='cancel_request'),
    path('change-password/', views.donor_change_password, name='change_password'),
    path('respond/<int:pk>/', views.respond_to_alert, name='respond_to_alert'),
    path('respond/<int:pk>/confirmation/', views.response_confirmation, name='response_confirmation'),
    path('sms/opened/<int:pk>/', views.mark_sms_opened, name='mark_sms_opened'),
    path('request-blood/', views.request_blood, name='request_blood'),
    path('request-blood/success/<int:pk>/', views.request_blood_success, name='request_blood_success'),
    
    # API endpoints
    path('api/urgent-alerts/', api_views.urgent_alerts, name='api_urgent_alerts'),
    path('api/notification-stats/', api_views.notification_stats, name='api_notification_stats'),
    path('api/toggle-availability/', api_views.toggle_availability, name='api_toggle_availability'),
    path('api/alerts/', api_views.get_alerts_list, name='api_alerts'),
    path('api/alerts/<int:alert_id>/respond/', api_views.respond_to_alert, name='api_respond_alert'),
    
    # Test page
    path('test/', views.test_page, name='test_page'),
    path('contact/', views.contact, name='contact'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    path('faq/', views.faq, name='faq'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('password-reset/', views.password_reset, name='password_reset'),
]
