# 🔐 BH Assurance Authentication System

A comprehensive, secure authentication system for the BH Assurance platform built with Django REST Framework and PostgreSQL.

## ✨ Features

### 🔑 **Core Authentication**
- **User Registration** with email verification
- **Secure Login/Logout** with token-based authentication
- **Password Management** (change, reset, strength validation)
- **Custom User Model** with extended fields

### 👤 **User Management**
- **User Types**: Client, User, Admin
- **Profile Management** (name, email, phone, bio, profile picture)
- **Account Status** (active, verified, staff)
- **UUID-based primary keys** for enhanced security

### 🛡️ **Security Features**
- **Session Management** with IP tracking and user agent logging
- **Token-based Authentication** with automatic cleanup
- **Password Strength Validation** with Django's built-in validators
- **CSRF Protection** and secure cookie settings
- **Rate Limiting Ready** (can be easily added)

### 📧 **Communication**
- **Email Verification** system
- **Password Reset** via email
- **Welcome Emails** for new users
- **Customizable Email Templates**

## 🏗️ **Architecture**

### **Models**
- `CustomUser` - Extended user model with additional fields
- `UserSession` - Track user sessions for security
- `PasswordResetToken` - Secure password reset tokens
- `EmailVerificationToken` - Email verification tokens

### **API Endpoints**
```
POST   /api/auth/register/                    - Register new user
POST   /api/auth/login/                       - Login user
POST   /api/auth/logout/                      - Logout user
GET    /api/auth/profile/                     - Get user profile
PUT    /api/auth/profile/update/              - Update user profile
POST   /api/auth/change-password/             - Change password
POST   /api/auth/request-password-reset/      - Request password reset
POST   /api/auth/confirm-password-reset/      - Confirm password reset
GET    /api/auth/sessions/                    - Get user sessions
DELETE /api/auth/sessions/{key}/terminate/    - Terminate session
DELETE /api/auth/sessions/terminate-all/      - Terminate all sessions
```

## 🚀 **Quick Start**

### **1. Setup**
```bash
# Run the setup script
python setup_auth.py

# Or manually:
python manage.py makemigrations authentication
python manage.py migrate
python manage.py createsuperuser
```

### **2. Start Server**
```bash
python manage.py runserver
```

### **3. Test API**
```bash
# Run automated tests
python test_auth_api.py

# Or import Postman collection
# BH_Assurance_Auth_API.postman_collection.json
```

## 📝 **API Usage Examples**

### **Register User**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "phone_number": "+1234567890",
    "user_type": "CLIENT",
    "password": "SecurePassword123!",
    "password_confirm": "SecurePassword123!"
  }'
```

### **Login User**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

### **Get Profile (Authenticated)**
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## 🔧 **Configuration**

### **Database Settings**
```python
# bhagent/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### **Email Settings**
```python
# For production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
DEFAULT_FROM_EMAIL = 'noreply@bhassurance.com'
```

### **Security Settings**
```python
# For production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

## 📊 **User Types**

| Type   | Description                    | Permissions                |
|--------|--------------------------------|----------------------------|
| CLIENT | Regular customers              | Basic profile management   |
| USER   | Internal users/employees       | Extended access            |
| ADMIN  | System administrators          | Full system access         |

## 🔒 **Security Best Practices**

### **Implemented**
- ✅ Password strength validation
- ✅ Token-based authentication
- ✅ Session tracking and management
- ✅ CSRF protection
- ✅ Secure cookie settings
- ✅ Input validation and sanitization
- ✅ SQL injection prevention (Django ORM)

### **Recommended for Production**
- 🔄 Rate limiting (django-ratelimit)
- 🔄 Two-factor authentication
- 🔄 Account lockout after failed attempts
- 🔄 IP whitelisting for admin accounts
- 🔄 Regular security audits

## 🧪 **Testing**

### **Automated Tests**
```bash
# Run API tests
python test_auth_api.py

# Run Django tests
python manage.py test authentication
```

### **Manual Testing**
1. Import `BH_Assurance_Auth_API.postman_collection.json` into Postman
2. Set the `base_url` variable to your server URL
3. Test all endpoints in sequence

## 📁 **File Structure**
```
authentication/
├── models.py              # User models and related models
├── serializers.py         # API serializers for validation
├── views.py              # API views and business logic
├── urls.py               # URL routing
├── admin.py              # Django admin configuration
├── utils.py              # Utility functions
├── apps.py               # App configuration
├── migrations/           # Database migrations
└── management/           # Custom management commands
    └── commands/
```

## 🚨 **Troubleshooting**

### **Common Issues**

**Migration Errors**
```bash
# Reset migrations if needed
python manage.py migrate authentication zero
python manage.py makemigrations authentication
python manage.py migrate
```

**Token Authentication Not Working**
- Ensure `rest_framework.authtoken` is in `INSTALLED_APPS`
- Check that `Authorization: Token <token>` header is included
- Verify token exists in database

**Database Connection Issues**
- Check PostgreSQL is running
- Verify database credentials in settings
- Ensure database exists

## 📞 **Support**

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation
3. Test with the provided Postman collection
4. Check Django logs for detailed error messages

## 🎉 **Success!**

Your BH Assurance Authentication System is now ready! 

- 🔐 Secure user authentication
- 👤 Complete user management
- 📧 Email integration ready
- 🛡️ Security best practices implemented
- 📱 API-first design for mobile/web integration
