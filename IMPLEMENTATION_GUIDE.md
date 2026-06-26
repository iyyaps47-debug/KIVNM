# 🔐 SkillzLearn Secure Authentication System

A modern, production-ready authentication and authorization system for the SkillzLearn Streamlit chatbot application.

## 📋 Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Reference](#api-reference)
7. [Security Features](#security-features)
8. [Admin Dashboard](#admin-dashboard)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Authentication & Authorization
- ✅ **User Registration** with email validation
- ✅ **Secure Login** with JWT tokens
- ✅ **Password Hashing** using bcrypt with salting
- ✅ **Session Management** with secure tokens
- ✅ **Remember Me** functionality
- ✅ **Password Reset** via email verification
- ✅ **Role-Based Access Control (RBAC)** with admin roles

### Security
- ✅ **Password Strength Validation** (uppercase, lowercase, digits, special chars)
- ✅ **Rate Limiting** for login attempts (5 failed attempts = 15 min lockout)
- ✅ **CSRF Protection** using CSRF tokens
- ✅ **SQL Injection Prevention** using parameterized queries
- ✅ **XSS Protection** with proper escaping
- ✅ **Secure Session Management** with expiration
- ✅ **Email Verification** for new accounts
- ✅ **Breach Detection** (Have I Been Pwned API integration)
- ✅ **Disposable Email Detection** to prevent spam signups

### User Management
- ✅ **User Profiles** with editable information
- ✅ **Email Verification** status tracking
- ✅ **Last Login** timestamp
- ✅ **Account Status** (active/inactive)
- ✅ **Password Change** functionality

### Admin Features
- ✅ **Admin Dashboard** with statistics
- ✅ **User Management** panel
- ✅ **Chat History** viewing (by admin)
- ✅ **Admin Audit Logs** for all actions
- ✅ **User Role Assignment**
- ✅ **Account Deactivation/Activation**

### UI/UX
- ✅ **Modern Responsive Design** with gradients
- ✅ **Dark Mode** support
- ✅ **Smooth Animations** and transitions
- ✅ **Mobile-Friendly** layout
- ✅ **Password Strength Meter**
- ✅ **Real-time Validation** feedback

---

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Streamlit, HTML, CSS, JavaScript
- **Backend**: Python 3.9+
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: Bcrypt
- **Encryption**: Fernet (AES-128)

### Project Structure
```
chatbot-auth-system/
├── app.py                    # Main Streamlit app
├── config.py                 # Configuration settings
├── database.py               # Database models and operations
├── auth_security.py          # Security utilities
├── validators.py             # Input validators
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    email_verified BOOLEAN DEFAULT 0,
    role TEXT DEFAULT 'user',  -- 'user', 'admin', 'superadmin'
    created_at TEXT,
    updated_at TEXT,
    last_login TEXT,
    profile_picture TEXT,
    bio TEXT,
    email_verification_token TEXT,
    password_reset_token TEXT,
    password_reset_expires TEXT
)
```

#### Login Attempts Table (Rate Limiting)
```sql
CREATE TABLE login_attempts (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    ip_address TEXT,
    attempt_time TEXT,
    success BOOLEAN
)
```

#### Sessions Table
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    created_at TEXT,
    expires_at TEXT,
    is_active BOOLEAN DEFAULT 1
)
```

#### Admin Logs Table
```sql
CREATE TABLE admin_logs (
    id INTEGER PRIMARY KEY,
    admin_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_user_id INTEGER,
    ip_address TEXT,
    timestamp TEXT,
    details TEXT
)
```

#### Chat History Table
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    message TEXT NOT NULL,
    response TEXT,
    timestamp TEXT
)
```

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/chatbot-auth-system.git
cd chatbot-auth-system
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your settings
# Generate a strong SECRET_KEY:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Initialize Database
```bash
python -c "from database import db; print('Database initialized successfully!')"
```

### Step 6: Run the Application
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

---

## ⚙️ Configuration

### Environment Variables (`.env`)

#### Essential Settings
```env
SECRET_KEY=your-generated-secret-key
DB_TYPE=sqlite  # or 'postgresql'
DATABASE_URL=sqlite:///chatbot_auth.db
```

#### Email Configuration (For Password Reset)
```env
EMAIL_PROVIDER=smtp
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password for Gmail
FROM_EMAIL=noreply@skillzlearn.com
```

#### Security Settings
```env
MIN_PASSWORD_LENGTH=8
REQUIRE_UPPERCASE=True
REQUIRE_LOWERCASE=True
REQUIRE_DIGITS=True
REQUIRE_SPECIAL_CHARS=True
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
```

#### Session Settings
```env
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SESSION_TIMEOUT_MINUTES=60
REMEMBER_ME_DAYS=30
```

---

## 📖 Usage

### Basic Login Flow
```python
from auth_security import PasswordManager, JWTManager
from validators import EmailValidator, PasswordValidator
from database import db

# Validate input
email_valid, msg = EmailValidator.validate("user@example.com")
password_valid, errors = PasswordValidator.validate("SecurePassword123!")

# Create user
user = db.create_user("John Doe", "john@example.com", "SecurePassword123!")

# Login user
user = db.get_user_by_email("john@example.com")
is_valid = PasswordManager.verify_password("SecurePassword123!", user.password_hash)

# Create JWT token
token = JWTManager.create_access_token({
    "user_id": user.id,
    "email": user.email,
    "role": user.role
})

# Verify token
payload = JWTManager.decode_token(token)
```

### Admin Functions
```python
from database import db

# Get all users
users = db.get_all_users()

# Get admin users
admins = db.get_all_users(role='admin')

# Log admin action
db.log_admin_action(
    admin_id=1,
    action="DELETE_USER",
    target_user_id=5,
    ip_address="192.168.1.1",
    details="Deleted inactive user"
)

# Delete user
db.delete_user(user_id=5)

# Update user role
db.update_user(user_id=2, role='admin')
```

---

## 🔗 API Reference

### Authentication Endpoints

#### POST /login
Login with email and password
```python
{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "remember_me": false
}

Response:
{
    "success": true,
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "user@example.com",
        "role": "user"
    }
}
```

#### POST /signup
Register new user
```python
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
}

Response:
{
    "success": true,
    "message": "Account created successfully"
}
```

#### POST /logout
Logout user
```python
Headers:
{
    "Authorization": "Bearer <token>"
}

Response:
{
    "success": true,
    "message": "Logged out successfully"
}
```

#### POST /password-reset
Request password reset
```python
{
    "email": "user@example.com"
}

Response:
{
    "success": true,
    "message": "Password reset email sent"
}
```

#### POST /password-reset/confirm
Confirm password reset with token
```python
{
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "new_password": "NewSecurePassword123!"
}

Response:
{
    "success": true,
    "message": "Password reset successfully"
}
```

### User Endpoints

#### GET /user/profile
Get current user profile
```python
Headers:
{
    "Authorization": "Bearer <token>"
}

Response:
{
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "user",
    "created_at": "2024-01-15T10:30:00",
    "last_login": "2024-01-20T14:45:00"
}
```

#### PUT /user/profile
Update user profile
```python
Headers:
{
    "Authorization": "Bearer <token>"
}

{
    "name": "Jane Doe",
    "bio": "New bio"
}

Response:
{
    "success": true,
    "user": {...}
}
```

#### POST /user/change-password
Change user password
```python
Headers:
{
    "Authorization": "Bearer <token>"
}

{
    "current_password": "OldPassword123!",
    "new_password": "NewPassword123!"
}

Response:
{
    "success": true,
    "message": "Password changed successfully"
}
```

### Admin Endpoints

#### GET /admin/users
Get all users (admin only)
```python
Headers:
{
    "Authorization": "Bearer <admin_token>"
}

Response:
{
    "users": [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "role": "user",
            "status": "active"
        }
    ]
}
```

#### GET /admin/user/{user_id}
Get specific user details (admin only)
```python
Response:
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "created_at": "2024-01-15",
    "last_login": "2024-01-20",
    "chat_history": [...]
}
```

#### PUT /admin/user/{user_id}
Update user (admin only)
```python
{
    "role": "admin",
    "is_active": true
}

Response:
{
    "success": true,
    "user": {...}
}
```

#### DELETE /admin/user/{user_id}
Delete user (admin only)
```python
Response:
{
    "success": true,
    "message": "User deleted successfully"
}
```

#### GET /admin/logs
Get admin action logs (admin only)
```python
Response:
{
    "logs": [
        {
            "id": 1,
            "admin_id": 1,
            "action": "DELETE_USER",
            "target_user_id": 5,
            "timestamp": "2024-01-20T14:30:00",
            "details": "Deleted inactive user"
        }
    ]
}
```

---

## 🔒 Security Features

### Password Security
- **Bcrypt Hashing** with 12-round salting
- **Strength Validation** requiring:
  - Minimum 8 characters
  - Uppercase letters (A-Z)
  - Lowercase letters (a-z)
  - Numbers (0-9)
  - Special characters (!@#$%^&*)
- **Breach Detection** using Have I Been Pwned API
- **Common Password Filtering** (password, 123456, etc.)

### Session Security
- **JWT Tokens** with 30-minute expiration
- **Refresh Tokens** with 7-day expiration
- **Session Tracking** with IP and user agent
- **Automatic Session Invalidation** on logout
- **Secure Session Storage** with encryption

### Rate Limiting
```python
# Max 5 failed login attempts per 15 minutes
# IP-based and email-based tracking
# Automatic account lockout after max attempts
```

### Input Validation
- **Email Validation** using email-validator library
- **Disposable Email Detection**
- **SQL Injection Prevention** via parameterized queries
- **XSS Protection** with proper escaping
- **CSRF Protection** using CSRF tokens

### Encryption
- **Password Reset Tokens** with 24-hour expiration
- **Email Verification Tokens**
- **Secure Password Encryption** using Fernet (AES-128)

### Audit Logging
- **Admin Action Logs** for all administrative activities
- **Login Attempt Tracking** for security monitoring
- **Session Activity Logging**
- **Timestamp Tracking** for all changes

---

## 👨‍💼 Admin Dashboard

### Admin Roles
- **admin**: Regular admin with full user management
- **superadmin**: Super admin with additional system access

### Admin Features

#### Dashboard
- Total users count
- Active users count
- Admin count
- Email verification statistics

#### User Management
- View all users
- View user profiles
- Edit user information
- Change user roles
- Activate/deactivate accounts
- Delete user accounts
- View user chat history

#### Chat History
- View all chat conversations
- Filter by user
- Filter by date range
- Search messages
- Export chat history

#### Admin Logs
- View all admin actions
- Filter by action type
- Filter by date range
- View detailed action information
- Track changes made by admins

### Default Admin Account
```
Email: admin@skillzlearn.com
Password: AdminPassword123!
```

⚠️ **Important**: Change default admin password after first login!

### Creating Additional Admins
```python
from database import db

# Create new admin user
admin = db.create_user(
    name="Admin Name",
    email="admin@example.com",
    password="SecureAdminPassword123!",
    role="admin"
)
```

---

## 🌐 Deployment

### Deployment to Streamlit Cloud

#### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add authentication system"
git push origin main
```

#### Step 2: Connect to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your GitHub repository
4. Set main file to `app.py`
5. Click "Deploy"

#### Step 3: Set Environment Variables in Streamlit Cloud
1. Go to app settings
2. Add secrets:
```toml
[secrets]
SECRET_KEY = "your-secret-key"
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
DB_TYPE = "sqlite"
```

### Production Deployment on Server

#### Step 1: Set up PostgreSQL (Recommended)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb chatbot_auth
sudo -u postgres psql
CREATE USER chatbot_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE chatbot_auth TO chatbot_user;
```

#### Step 2: Update .env for Production
```env
DB_TYPE=postgresql
DB_USER=chatbot_user
DB_PASSWORD=strong_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=chatbot_auth
SECRET_KEY=<generate-new-secret-key>
DEBUG=False
```

#### Step 3: Deploy with Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

Build and run:
```bash
docker build -t chatbot-auth .
docker run -p 8501:8501 --env-file .env chatbot-auth
```

#### Step 4: Use Reverse Proxy (Nginx)
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Database is locked" Error
**Solution**: SQLite locks when multiple processes access it simultaneously. Use PostgreSQL for production.

```python
# Switch to PostgreSQL in .env
DB_TYPE=postgresql
```

#### 2. Email Not Sending
**Solution**: Check SMTP credentials and enable "Less secure app access" for Gmail.

```env
# For Gmail, use App Password instead of regular password
SMTP_PASSWORD=your-16-character-app-password
```

#### 3. Password Reset Token Expired
**Solution**: Token expires after 24 hours. User needs to request new reset.

#### 4. Login Rate Limiting Issue
**Solution**: Wait 15 minutes after 5 failed attempts, or clear login attempts:

```python
from database import db
# Wait 15 minutes automatically
```

#### 5. Session Expires Too Quickly
**Solution**: Adjust in .env:

```env
ACCESS_TOKEN_EXPIRE_MINUTES=60  # Increase from 30
SESSION_TIMEOUT_MINUTES=120      # Increase from 60
```

### Debug Mode

Enable debug logging:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

View logs:
```bash
tail -f app.log
```

---

## 📊 Performance Optimization

### Database Optimization
```python
# Add indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_login_attempts_email ON login_attempts(email);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
```

### Caching
```python
import streamlit as st

@st.cache_data(ttl=3600)
def get_user_stats():
    return db.get_all_users()
```

### Connection Pooling
```python
# For PostgreSQL, use connection pool
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
```

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Support

For issues and questions:
1. Check Troubleshooting section
2. Review API Reference
3. Check GitHub Issues
4. Contact: support@skillzlearn.com

---

## 🎯 Roadmap

- [ ] 2FA (Two-Factor Authentication)
- [ ] Social Login (Google, GitHub)
- [ ] OAuth2 Integration
- [ ] SAML Support
- [ ] Advanced Audit Logging
- [ ] User Activity Dashboard
- [ ] Email Notification System
- [ ] SMS Verification
- [ ] Biometric Authentication

---

**Created for SkillzLearn | Secure Education Platform**
