# BloodLink - Emergency Blood Donation System

BloodLink is a comprehensive blood donation management system for St. Francis Hospital Nsambya, Uganda. The system connects blood donors with emergency blood requests in real-time, helping save lives through efficient blood donation coordination.

## 🩸 Features

### For Donors
- **Online Registration**: Easy donor registration with medical history
- **Emergency Alerts**: Real-time SMS and push notifications for blood requests
- **Dashboard**: Personal donation history and statistics
- **Availability Management**: Set donation availability status
- **Mobile Responsive**: Works on all devices

### For Hospital Staff
- **Emergency Requests**: Create and manage urgent blood requests
- **Donor Management**: Comprehensive donor database with blood type matching
- **SMS Notifications**: Automated alerts to matching donors
- **Real-time Tracking**: Monitor notification delivery and donor responses
- **Analytics**: Detailed reports and statistics
- **Push Notifications**: Web push alerts alongside SMS system

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 4.2+
- PostgreSQL (for production)
- Africa's Talking API account for SMS

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ainebyemartin0-arch/BloodLink.git
   cd BloodLink
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

## 🔐 Access URLs

- **Donor Portal**: `/donor/`
- **Staff Login**: `/staff/secure-access/` (keep this URL private)
- **Admin**: Disabled for security (Python 3.14 compatibility)

## 📱 SMS Configuration

The system uses Africa's Talking API for SMS notifications. Configure these in your `.env`:

```
AT_USERNAME=your_username
AT_API_KEY=your_api_key
AT_SENDER_ID=BloodLink
```

## 🔔 Push Notifications

Web push notifications are configured using VAPID keys:

```
VAPID_PRIVATE_KEY=your_private_key
VAPID_PUBLIC_KEY=your_public_key
VAPID_CLAIMS_EMAIL=admin@bloodlink.ug
```

## 🗄️ Database Setup

### Development (SQLite)
```bash
python manage.py migrate
```

### Production (PostgreSQL)
Update your `.env` with database credentials:
```
DB_NAME=bloodlink_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
```

## 🚀 Deployment

### Render.com Deployment
1. Connect your GitHub repository to Render
2. Configure environment variables in Render dashboard
3. Deploy automatically on push to main branch

### Static Files
```bash
python manage.py collectstatic --noinput
```

## 🧪 Testing

### Test SMS API
Visit `/notifications/test-sms-api/` to test Africa's Talking connection

### Test Push Notifications
1. Visit donor dashboard
2. Click "Enable Emergency Alerts"
3. Allow browser notifications
4. Create emergency request to test

## 📊 System Architecture

### Models
- **Donor**: Donor information and medical history
- **EmergencyRequest**: Blood request details
- **SMSNotification**: SMS delivery tracking
- **PushSubscription**: Web push notification subscriptions

### Features
- **Blood Type Matching**: Automatic donor filtering by blood type
- **Real-time Notifications**: SMS + Web push alerts
- **Response Tracking**: Monitor donor responses to requests
- **Analytics Dashboard**: Comprehensive reporting

## 🔒 Security Features

- **Hidden Staff Login**: Staff login URL is private (`/staff/secure-access/`)
- **No Public Admin**: Django admin disabled for security
- **CSRF Protection**: All forms protected
- **Input Validation**: Comprehensive form validation
- **Session Security**: Secure session management

## 🎨 UI/UX Enhancements

- **React-Quality Animations**: Smooth page transitions and micro-interactions
- **Toast Notifications**: Modern notification system
- **Skeleton Loading**: Professional loading states
- **Responsive Design**: Mobile-first approach
- **Interactive Elements**: Blood type selector, hover effects
- **Parallax Effects**: Dynamic scrolling animations

## 📱 Mobile Support

- **Progressive Web App**: Works offline-capable
- **Push Notifications**: Browser-based alerts
- **Responsive Design**: Optimized for all screen sizes
- **Touch-Friendly**: Large tap targets and gestures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏥 About St. Francis Hospital Nsambya

St. Francis Hospital Nsambya is a leading healthcare provider in Uganda, committed to saving lives through quality medical care and community health initiatives.

## 📞 Support

For technical support:
- **Email**: admin@bloodlink.ug
- **GitHub Issues**: [Create an issue](https://github.com/ainebyemartin0-arch/BloodLink/issues)

---

**BloodLink © 2026 — St. Francis Hospital Nsambya**  
*Connecting donors with those in need, one blood donation at a time.*
