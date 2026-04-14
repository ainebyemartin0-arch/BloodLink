from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('<int:pk>/update-response/', views.update_response, name='update_response'),
    path('test-connection/', views.test_connection, name='test_connection'),
    path('test-sms-api/', views.test_sms_api, name='test_sms_api'),
]
