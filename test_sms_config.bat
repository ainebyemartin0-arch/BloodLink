@echo off
echo Testing Africa's Talking Configuration...
echo.

REM Check if environment variables are set
echo Current Configuration:
echo AT_USERNAME: %AT_USERNAME%
echo AT_API_KEY: %AT_API_KEY%
echo AT_SENDER_ID: %AT_SENDER_ID%
echo.

REM Test the connection
python manage.py shell -c "from notifications.utils import test_africastalking_connection; result = test_africastalking_connection(); print('Connection Test Result:'); print(result)"

echo.
echo If the test shows 'success': True, your configuration is working!
echo If it shows 'success': False, check your credentials and try again.
pause
