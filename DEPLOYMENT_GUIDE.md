# BloodLink Deployment Guide - Render.com

## 🚀 Quick Deployment Steps

### 1. **Connect Your Repository**
- Go to your Render dashboard: https://dashboard.render.com/
- Click "New +" → "Web Service"
- Connect your GitHub repository containing BloodLink

### 2. **Configure Deployment**
- **Name**: `bloodlink`
- **Region**: Choose nearest region
- **Branch**: `main` (or your default branch)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start Command**: `gunicorn bloodlink_project.wsgi:application --log-file -`

### 3. **Environment Variables**
Add these environment variables in Render dashboard:

```bash
DEBUG=False
SECRET_KEY=[generate-random-key]
ALLOWED_HOSTS=.onrender.com localhost 127.0.0.1
DATABASE_URL=[auto-generated-by-render]
AT_USERNAME=sandbox
AT_API_KEY=atsk_d7bad867730125e077fcf34902a3e45107e87d8cfd5b8336c1642fc34bccd4b0a4ed14bf
AT_SENDER_ID=BloodLink
PYTHON_VERSION=3.11.9
```

### 4. **Database Setup**
- Add PostgreSQL database (free tier available)
- Render will automatically set `DATABASE_URL`

### 5. **Deploy**
- Click "Create Web Service"
- Wait for deployment to complete (2-5 minutes)
- Your app will be available at: `https://bloodlink.onrender.com`

## 🔧 Configuration Files

### render.yaml (Already Configured)
Your `render.yaml` file is already set up with:
- Web service configuration
- Database setup
- Environment variables
- Build and start commands

### Django Settings (Already Configured)
- Production settings in `bloodlink_project/settings.py`
- Static files handling with WhiteNoise
- Database URL parsing
- Security settings enabled

## 📋 Pre-Deployment Checklist

### ✅ Files Ready
- [x] `render.yaml` - Deployment configuration
- [x] `requirements.txt` - Python dependencies
- [x] `wsgi.py` - WSGI application entry point
- [x] `settings.py` - Production settings configured
- [x] Static files configured with WhiteNoise

### ✅ Features Ready
- [x] Blood stock monitoring system
- [x] Donor eligibility management
- [x] Staff dashboard with alerts
- [x] Hero image carousel
- [x] Professional UI/UX
- [x] SMS notifications (Africa's Talking)
- [x] Real-time updates

## 🌐 Post-Deployment Steps

### 1. **Test Your Application**
- Visit your deployed URL
- Test donor registration and login
- Test staff login and dashboard
- Verify blood stock monitoring
- Test request creation and management

### 2. **Create Superuser**
```bash
# In Render dashboard, go to your service → Shell
python manage.py createsuperuser
```

### 3. **Initialize Blood Stocks**
```bash
python manage.py init_blood_stocks
```

### 4. **Setup Initial Data**
```bash
python manage.py setup_initial_data
```

## 🔒 Security Notes

### ✅ Security Features Enabled
- DEBUG=False in production
- SECRET_KEY generated randomly
- ALLOWED_HOSTS configured for Render domains
- Database URL from environment variable
- Static files served securely
- CSRF protection enabled

### 🔐 Recommended Actions
- Change default admin credentials
- Monitor database usage (free tier limits)
- Set up monitoring and alerts
- Regular backups (paid tiers only)

## 📱 Features Available After Deployment

### 🩸 **Donor Portal**
- Registration and login
- Blood request viewing
- Eligibility status
- Professional UI with carousel

### 👨‍⚕️ **Staff Portal**
- Dashboard with real-time stats
- Blood stock monitoring
- Request management
- SMS notifications
- Professional medical interface

### 🔄 **Real-time Features**
- Live stock level updates
- Automated alerts
- Donor eligibility tracking
- Request status updates

## 🆘 Troubleshooting

### Common Issues & Solutions

#### 1. **Build Fails**
- Check `requirements.txt` for correct versions
- Verify all dependencies are compatible
- Check build logs in Render dashboard

#### 2. **Static Files Not Loading**
- Ensure `collectstatic` runs in build command
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Verify WhiteNoise is properly configured

#### 3. **Database Connection Issues**
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL database status
- Ensure migrations run successfully

#### 4. **500 Internal Server Error**
- Check Render logs for specific errors
- Verify all environment variables are set
- Ensure WSGI configuration is correct

## 💡 Pro Tips

### 🚀 Performance Optimization
- Use Redis for session storage (paid tier)
- Enable database connection pooling
- Optimize static file delivery
- Monitor resource usage

### 📊 Monitoring
- Set up uptime monitoring
- Track error rates
- Monitor database performance
- Set up alert notifications

### 🔄 Updates
- Push updates to main branch
- Render auto-deploys on push
- Test in staging first
- Monitor deployment health

## 🎉 Success Metrics

Your BloodLink deployment is successful when:
- ✅ Application loads without errors
- ✅ Donor registration works
- ✅ Staff login functions
- ✅ Blood stock monitoring displays
- ✅ SMS notifications send
- ✅ All features work as expected

## 📞 Support

If you encounter issues:
1. Check Render logs
2. Verify environment variables
3. Test locally with same settings
4. Review this guide
5. Contact Render support (platform issues)

---

**🎊 Your BloodLink system is ready for professional deployment!**

**Deploy URL**: https://bloodlink.onrender.com (after deployment)
**Admin URL**: https://bloodlink.onrender.com/admin
**Staff Portal**: https://bloodlink.onrender.com/staff/
**Donor Portal**: https://bloodlink.onrender.com/donor/
