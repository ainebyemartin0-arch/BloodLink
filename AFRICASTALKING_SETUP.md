# Africa's Talking SMS Configuration for BloodLink
# Follow these steps to configure your credentials:

## 1. Get Your Africa's Talking Credentials
# - Login to https://account.africastalking.com/
# - Go to Settings → API Key
# - Copy your API Key and Username

## 2. Set Environment Variables in Windows

### Method 1: Using PowerShell (Temporary - Current Session Only)
$env:AT_USERNAME = "your_username_here"
$env:AT_API_KEY = "your_api_key_here" 
$env:AT_SENDER_ID = "BloodLink"

### Method 2: Using Command Prompt (Temporary)
set AT_USERNAME=your_username_here
set AT_API_KEY=your_api_key_here
set AT_SENDER_ID=BloodLink

### Method 3: Windows GUI (Permanent)
1. Press Windows Key + R
2. Type "sysdm.cpl" and press Enter
3. Go to "Advanced" tab
4. Click "Environment Variables..."
5. Under "User variables", click "New..."
6. Add these variables:
   - Variable name: AT_USERNAME
   - Variable value: your_username_here
7. Click "New..." again:
   - Variable name: AT_API_KEY  
   - Variable value: your_api_key_here
8. Click "New..." again:
   - Variable name: AT_SENDER_ID
   - Variable value: BloodLink
9. Click OK on all windows
10. Restart your terminal/IDE

## 3. Test Your Configuration
# After setting variables, restart your Django server and test:
python manage.py shell -c "from notifications.utils import test_africastalking_connection; result = test_africastalking_connection(); print(result)"

## 4. Important Notes
- Your API Key should be kept secret - don't share it
- Username is usually your email address or account username
- Sender ID may need to be approved by Africa's Talking
- Test with small amounts first (SMS costs money)
- Uganda phone numbers should be in +256 format

## 5. Troubleshooting
If SMS still fails:
1. Check your Africa's Talking account balance
2. Verify your phone number format (+256...)
3. Ensure your Sender ID is approved
4. Check Africa's Talking dashboard for error logs
5. Contact Africa's Talking support if needed
