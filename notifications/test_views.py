from django.http import JsonResponse
from .utils import test_africastalking_connection

def test_sms_api(request):
    """Public test endpoint for Africa's Talking API."""
    result = test_africastalking_connection()
    return JsonResponse(result)
