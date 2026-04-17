# BloodLink Staff Registration & Login Guide

## Overview
BloodLink provides a secure staff registration and login system for hospital personnel. This guide explains how staff members can register for accounts and access the system.

## Registration Process

### 1. Public Staff Registration
Any hospital staff member can register for an account online.

**URL:** `http://127.0.0.1:8000/staff/register/`

**Required Information:**
- **Personal Details:** First Name, Last Name
- **Account Information:** Username, Email Address
- **Professional Details:** Designation, Department, Phone Number
- **Security:** Password (minimum 8 characters), Confirm Password

**Registration Steps:**
1. Go to the registration page
2. Fill in all required fields accurately
3. Choose a strong password (8+ characters)
4. Click "Register Account"
5. Wait for admin approval

### 2. Account Approval Process
- **Automatic Submission:** Registration goes into pending status
- **Admin Review:** System administrator reviews the registration
- **Approval/Rejection:** Admin can approve or reject the registration
- **Notification:** User receives email notification of the decision

### 3. Available Staff Designations
- **Laboratory Technician** - Lab staff and blood bank personnel
- **Blood Bank Administrator** - Blood bank management
- **Emergency Unit Clinician** - Emergency department staff
- **IT Staff** - Technical support personnel
- **System Administrator** - System management and administration

## Login Process

### 1. Accessing the Login Page
**URL:** `http://127.0.0.1:8000/staff/secure-access/`

### 2. Login Credentials
- **Username:** Your chosen username (provided during registration)
- **Password:** Your password (set during registration)

### 3. Default System Credentials
For initial system access:
- **Username:** `bloodlink_admin`
- **Password:** `superadmin123`
- **Role:** System Administrator

### 4. Login Features
- **Password Visibility Toggle:** Click the eye icon to show/hide password
- **Remember Me:** Browser can remember login session
- **Error Handling:** Clear messages for incorrect credentials
- **Loading States:** Visual feedback during authentication

## Account Management

### 1. For New Staff Members
1. **Register:** Complete the registration form
2. **Wait for Approval:** Admin will review your registration
3. **Check Email:** You'll receive approval notification
4. **Login:** Use your credentials to access the system

### 2. For Administrators
1. **Access Approval Panel:** Go to `/staff/approve-staff/`
2. **Review Registrations:** See all pending staff registrations
3. **Approve/Reject:** Accept or deny registrations
4. **Manage Accounts:** Full control over staff access

### 3. Account Status Types
- **Pending:** Registration submitted, awaiting approval
- **Active:** Approved and can access the system
- **Inactive:** Deactivated or rejected
- **Approved:** Registration approved by administrator

## Security Features

### 1. Password Requirements
- Minimum 8 characters
- Can include letters, numbers, and special characters
- Password strength validation during registration

### 2. Account Security
- **Approval System:** All registrations require admin approval
- **Session Management:** Secure login sessions
- **Activity Logging:** All actions are logged for audit
- **Role-Based Access:** Different access levels by designation

### 3. Login Protection
- **CSRF Protection:** Prevents cross-site request forgery
- **Secure Authentication:** Django's built-in security
- **Error Handling:** No information disclosure for failed attempts

## Troubleshooting

### 1. Registration Issues
- **Email Already Used:** Each email can only be used once
- **Username Taken:** Choose a unique username
- **Password Too Weak:** Use at least 8 characters
- **Form Validation:** Ensure all required fields are filled

### 2. Login Issues
- **Incorrect Credentials:** Check username and password
- **Account Not Approved:** Wait for admin approval
- **Account Deactivated:** Contact system administrator
- **Browser Issues:** Try clearing cache or using different browser

### 3. Approval Issues
- **No Admin Access:** Only superusers can approve accounts
- **Missing Registrations:** Check pending registrations list
- **Email Notifications:** Ensure email settings are configured

## URL Reference

| Purpose | URL | Access Level |
|---------|-----|--------------|
| Staff Login | `/staff/secure-access/` | Public |
| Staff Registration | `/staff/register/` | Public |
| Admin Registration | `/staff/register-admin/` | Superuser Only |
| Approval Panel | `/staff/approve-staff/` | Superuser Only |
| Staff Dashboard | `/staff/dashboard/` | Authenticated Staff |
| Logout | `/staff/logout/` | Authenticated Staff |

## Admin Quick Start

### 1. Initial Setup
1. Login with default credentials: `bloodlink_admin` / `superadmin123`
2. Go to dashboard: `/staff/dashboard/`
3. Access approval panel: `/staff/approve-staff/`

### 2. Staff Management
1. **Approve Registrations:** Review and approve pending staff
2. **Direct Registration:** Use admin registration for immediate access
3. **Monitor Activity:** Check activity logs for system usage
4. **Manage Access:** Control who can access the system

### 3. Best Practices
- **Verify Identity:** Ensure registrations are from legitimate staff
- **Appropriate Designations:** Assign correct roles and permissions
- **Regular Reviews:** Periodically review staff access
- **Security Awareness:** Keep credentials secure and private

## Support

For technical issues or questions:
- **IT Department:** Contact hospital IT staff
- **System Administrator:** Email admin@bloodlink.ug
- **Emergency Support:** Use hospital IT helpdesk

---

*This guide is for St. Francis Hospital Nsambya BloodLink System. For the most current information, contact the system administrator.*
