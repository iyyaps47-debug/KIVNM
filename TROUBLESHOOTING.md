# 🆘 Troubleshooting & FAQ

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Database Issues](#database-issues)
3. [Authentication Issues](#authentication-issues)
4. [Email Issues](#email-issues)
5. [Deployment Issues](#deployment-issues)
6. [Performance Issues](#performance-issues)
7. [Security Concerns](#security-concerns)
8. [General FAQ](#general-faq)

---

## Installation Issues

### ❌ "ModuleNotFoundError: No module named 'streamlit'"

**Problem**: Required packages not installed

**Solution**:
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install all requirements
pip install -r requirements.txt

# Or install individually
pip install streamlit bcrypt PyJWT email-validator cryptography
```

**Verify installation**:
```bash
python -c "import streamlit; print(streamlit.__version__)"
```

---

### ❌ "Python 3.9 or higher required"

**Problem**: Your Python version is too old

**Solution**:
```bash
# Check your Python version
python --version

# Download Python 3.9+ from python.org
# Or use version manager:
# macOS: brew install python@3.9
# Linux: apt-get install python3.9
```

---

### ❌ "Permission denied" when running setup

**Problem**: Permission issues on Linux/macOS

**Solution**:
```bash
# Make script executable
chmod +x setup.py

# Run with python explicitly
python setup.py

# Or use sudo if needed (not recommended)
sudo python setup.py
```

---

## Database Issues

### ❌ "Database is locked" Error

**Problem**: Multiple Streamlit processes accessing SQLite simultaneously

**Solution**:
```bash
# 1. Stop all running instances
# Press Ctrl+C in terminal

# 2. Delete lock file (if exists)
rm chatbot_auth.db-wal
rm chatbot_auth.db-shm

# 3. Use PostgreSQL for production (recommended)
# See IMPLEMENTATION_GUIDE.md for PostgreSQL setup
```

---

### ❌ "Unable to connect to database"

**Problem**: Database URL is incorrect or database doesn't exist

**Solution**:
```bash
# For SQLite
# Check if file exists
ls -la chatbot_auth.db

# Reset database
rm chatbot_auth.db
python -c "from database import db; print('Database initialized')"

# For PostgreSQL
# Verify connection string in .env
# Format: postgresql://user:password@host:port/database

# Test connection
psql postgresql://user:password@localhost:5432/chatbot_auth
```

---

### ❌ "Table 'users' doesn't exist"

**Problem**: Database not initialized properly

**Solution**:
```bash
# Reinitialize database
python -c "from database import db; print('Database initialized')"

# Or run setup script
python setup.py
```

---

## Authentication Issues

### ❌ "Invalid email or password" but credentials are correct

**Problem**: Could be several issues:
1. Email is case-sensitive in the database
2. Password hash is corrupted
3. User account is inactive

**Solution**:
```bash
# Check if user exists
sqlite3 chatbot_auth.db "SELECT * FROM users WHERE email='admin@skillzlearn.com';"

# Check if account is active
sqlite3 chatbot_auth.db "SELECT is_active FROM users WHERE email='admin@skillzlearn.com';"

# If inactive, activate it
sqlite3 chatbot_auth.db "UPDATE users SET is_active=1 WHERE email='admin@skillzlearn.com';"

# If password is forgotten, reset database
rm chatbot_auth.db
python setup.py
```

---

### ❌ "Too many login attempts" when trying to login

**Problem**: Account is locked due to failed login attempts (security feature)

**Solution**:
```bash
# Wait 15 minutes (default lockout duration)
# Or clear login attempts manually
sqlite3 chatbot_auth.db "DELETE FROM login_attempts WHERE email='user@example.com';"

# Increase lockout duration if needed (in .env)
LOCKOUT_DURATION_MINUTES=30
```

---

### ❌ Token expired immediately

**Problem**: Token expiration time is too short or system clock is wrong

**Solution**:
```env
# In .env, increase token duration
ACCESS_TOKEN_EXPIRE_MINUTES=60  # Increase from 30
REFRESH_TOKEN_EXPIRE_DAYS=14    # Increase from 7
```

---

### ❌ "Unauthorized: Admin privileges required"

**Problem**: User is not an admin but trying to access admin features

**Solution**:
```bash
# Make user an admin
sqlite3 chatbot_auth.db "UPDATE users SET role='admin' WHERE email='user@example.com';"

# Or in Streamlit:
# Login as admin, then use admin panel to change user role
```

---

## Email Issues

### ❌ "SMTP authentication failed"

**Problem**: Email credentials are incorrect

**Solution**:
```bash
# For Gmail:
# 1. Go to myaccount.google.com/apppasswords
# 2. Select Mail and Windows Computer
# 3. Generate App Password (16 characters)
# 4. Use that password in .env

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password

# For other providers:
# Gmail: smtp.gmail.com:587
# Yahoo: smtp.mail.yahoo.com:587
# Outlook: smtp-mail.outlook.com:587
# Custom: Check your provider's documentation
```

---

### ❌ "Email not sent"

**Problem**: Email configuration is not set up

**Solution**:
```bash
# Verify email settings in .env
grep "SMTP" .env

# Make sure these are set:
# SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

# Test connection manually
python -c "
import smtplib
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@gmail.com', 'your-password')
    print('Email configured correctly')
except Exception as e:
    print(f'Error: {e}')
"
```

---

### ❌ "Email verification not working"

**Problem**: Email verification feature not enabled or configured

**Solution**:
```env
# Enable email verification
ENABLE_EMAIL_VERIFICATION=True

# Configure SMTP (see above)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## Deployment Issues

### ❌ "App fails on Streamlit Cloud"

**Problem**: Secrets not configured or dependencies missing

**Solution**:
1. Go to https://share.streamlit.io
2. Click on app settings
3. Add these secrets:
```toml
[secrets]
SECRET_KEY = "your-generated-secret-key"
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
DB_TYPE = "sqlite"
DEBUG = "False"
```

4. Redeploy app

---

### ❌ "Database file not found" on deployment

**Problem**: Relative path is wrong in deployment environment

**Solution**:
```python
# In database.py, use absolute path
import os
from pathlib import Path

if os.environ.get('DEPLOYMENT_ENV') == 'cloud':
    DB_PATH = '/tmp/chatbot_auth.db'  # Temp file for cloud
else:
    DB_PATH = 'chatbot_auth.db'  # Local path
```

---

### ❌ "CORS error" when calling API

**Problem**: Cross-origin request is blocked

**Solution**:
```python
# In config.py, update CORS settings
CORS_ORIGINS = [
    "http://localhost:8501",
    "http://localhost:3000",
    "https://yourdomain.com",
    "https://kinvcreation4655.streamlit.app"
]
```

---

## Performance Issues

### ❌ "App is slow / freezing"

**Problem**: Could be SQLite contention or large queries

**Solution**:
```bash
# 1. Switch to PostgreSQL
DB_TYPE=postgresql

# 2. Add database indexes
sqlite3 chatbot_auth.db "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);"
sqlite3 chatbot_auth.db "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);"

# 3. Clear old data
sqlite3 chatbot_auth.db "DELETE FROM login_attempts WHERE attempt_time < datetime('now', '-30 days');"

# 4. Optimize queries in code
# Add LIMIT clauses, use indexes, etc.
```

---

### ❌ "Memory leak" or increasing memory usage

**Problem**: Sessions or cache not being cleared

**Solution**:
```python
# In session_manager, add cleanup
def cleanup_expired_sessions(self):
    current_time = datetime.utcnow()
    expired_sessions = [
        sid for sid, sess in self.sessions.items()
        if (current_time - sess['created_at']).seconds > 3600
    ]
    for sid in expired_sessions:
        del self.sessions[sid]

# Call periodically
import schedule
schedule.every(1).hour.do(session_manager.cleanup_expired_sessions)
```

---

## Security Concerns

### ❌ "Secret Key is exposed"

**Problem**: SECRET_KEY was committed to git or visible in logs

**Solution**:
```bash
# 1. Generate new secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Update .env
SECRET_KEY=<new-generated-key>

# 3. If committed to git, rotate it
# All existing tokens will be invalidated

# 4. Never commit .env file
# Use .env.example as template instead
echo ".env" >> .gitignore
git rm --cached .env
```

---

### ❌ "Password is visible in logs"

**Problem**: Debug logging is enabled with sensitive data

**Solution**:
```env
# Set debug to false in production
DEBUG=False
LOG_LEVEL=WARNING  # Don't log sensitive data
```

---

## General FAQ

### Q: How do I reset the admin password?

**A**: 
```bash
# Option 1: Delete database and start fresh
rm chatbot_auth.db
python setup.py

# Option 2: Reset via database
sqlite3 chatbot_auth.db
UPDATE users SET password_hash = '<new_bcrypt_hash>' WHERE email='admin@skillzlearn.com';

# Option 3: Use password reset email feature
# Navigate to /forgot-password page
```

---

### Q: Can I use the same database for multiple chatbots?

**A**: 
```python
# Not recommended - each chatbot should have its own auth system
# If you must share:
# Use different table prefixes: chatbot1_users, chatbot2_users
# Or use different databases: chatbot_auth_1, chatbot_auth_2

# Better approach: Use central auth service
# All chatbots hit the same API for authentication
```

---

### Q: How do I delete a user account?

**A**:
```bash
# Option 1: Via admin dashboard
# Login as admin → Users → Delete

# Option 2: Via database
sqlite3 chatbot_auth.db "DELETE FROM users WHERE email='user@example.com';"

# This will also delete their:
# - Login attempts
# - Sessions
# - Chat history
```

---

### Q: How do I export user data?

**A**:
```bash
# Export all users to CSV
sqlite3 chatbot_auth.db ".mode csv" "SELECT * FROM users;" > users_export.csv

# Export chat history
sqlite3 chatbot_auth.db ".mode csv" "SELECT * FROM chat_history;" > chat_export.csv

# Export admin logs
sqlite3 chatbot_auth.db ".mode csv" "SELECT * FROM admin_logs;" > admin_logs_export.csv
```

---

### Q: How do I backup my database?

**A**:
```bash
# Manual backup
cp chatbot_auth.db chatbot_auth.db.backup.$(date +%Y%m%d_%H%M%S)

# Automated backup script
#!/bin/bash
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR
cp chatbot_auth.db $BACKUP_DIR/chatbot_auth.db.backup.$(date +%Y%m%d_%H%M%S)

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.backup.*" -mtime +30 -delete

# Add to crontab for daily backups
# 0 2 * * * /path/to/backup_script.sh
```

---

### Q: How do I migrate from SQLite to PostgreSQL?

**A**:
```bash
# 1. Set up PostgreSQL (see IMPLEMENTATION_GUIDE.md)
# 2. Run migration script
python migrate_to_postgresql.py

# Migration script:
import sqlite3
import psycopg2
from database import Database

# Connect to both databases
sqlite_db = sqlite3.connect('chatbot_auth.db')
pg_db = psycopg2.connect("postgresql://user:password@localhost/chatbot_auth")

# Copy tables
sqlite_cursor = sqlite_db.cursor()
pg_cursor = pg_db.cursor()

# Copy users
sqlite_cursor.execute("SELECT * FROM users")
for row in sqlite_cursor.fetchall():
    pg_cursor.execute("INSERT INTO users VALUES (%s, %s, ...)", row)

pg_db.commit()
pg_cursor.close()
sqlite_cursor.close()
```

---

### Q: How do I enable HTTPS in development?

**A**:
```bash
# Install mkcert
# macOS: brew install mkcert
# Linux: sudo apt-get install mkcert
# Windows: choco install mkcert

# Create certificate
mkcert localhost 127.0.0.1 ::1

# Update streamlit config (.streamlit/config.toml)
[client]
serverAddress = "localhost"

[server]
sslKeyFile = "localhost-key.pem"
sslCertFile = "localhost.pem"
```

---

### Q: How do I integrate with external APIs?

**A**:
```python
# Example: Call external chatbot API
import requests

def call_chatbot_api(message, user_id):
    headers = {
        'Authorization': f'Bearer {st.session_state.token}',
        'User-ID': str(user_id)
    }
    
    response = requests.post(
        'https://api.chatbot.com/chat',
        json={'message': message},
        headers=headers,
        timeout=10
    )
    
    return response.json()
```

---

### Q: What's the maximum number of concurrent users?

**A**: 
- SQLite: ~100-1000 (single file database, not suitable for concurrent access)
- PostgreSQL: 1000+ (depends on server resources)
- Recommended: Use PostgreSQL for production with proper connection pooling

---

### Q: How do I handle 2FA?

**A**: 
See roadmap in IMPLEMENTATION_GUIDE.md. Not yet implemented. You can:
1. Use third-party service (Twilio, Authy)
2. Implement TOTP (Time-based One-Time Password)
3. Use email-based OTP

---

## Getting More Help

1. **Check logs**: `tail -f app.log`
2. **Check database**: `sqlite3 chatbot_auth.db`
3. **Review code**: Check `app.py`, `database.py`, `auth_security.py`
4. **Run tests**: `python -m pytest`
5. **Debug mode**: Set `DEBUG=True` in .env
6. **Contact support**: support@skillzlearn.com

---

**Still having issues? Check the IMPLEMENTATION_GUIDE.md or INTEGRATION_GUIDE.md for more details!**
