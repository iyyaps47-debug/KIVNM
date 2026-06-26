# 🚀 Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Python 3.9+
- pip
- Git (optional)

### Step 1: Clone or Download Files (1 min)
```bash
git clone https://github.com/yourusername/chatbot-auth-system.git
cd chatbot-auth-system
```

### Step 2: Create Virtual Environment (1 min)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies (2 min)
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment (30 sec)
```bash
# Copy example config
cp .env.example .env

# Generate a secret key for your environment
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
```

### Step 5: Run the App (30 sec)
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` 🎉

---

## Default Credentials

After first run, you can login with:

**Admin Account:**
- Email: `admin@skillzlearn.com`
- Password: `AdminPassword123!`

**⚠️ IMPORTANT**: Change these credentials after first login!

---

## Next Steps

### 1. Change Default Admin Password
1. Login with admin account
2. Go to Settings
3. Change password to something secure

### 2. Create First User Account
1. Go to Signup page
2. Fill in your details
3. Complete email verification

### 3. Configure Email (Optional)
To enable password reset emails:

```env
# Gmail example
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password, not regular password
FROM_EMAIL=noreply@skillzlearn.com
```

For Gmail, generate an [App Password](https://myaccount.google.com/apppasswords)

### 4. Set Up Database (Production)
Switch to PostgreSQL for production:

```env
DB_TYPE=postgresql
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=chatbot_auth
```

Create database:
```sql
CREATE DATABASE chatbot_auth;
```

---

## Testing the System

### Test 1: Sign Up
1. Click "Sign up here" on login page
2. Enter name, email, password
3. Click "Create Account"
4. You should see success message

### Test 2: Login
1. Click login page
2. Enter email and password
3. Click "Login"
4. You should be redirected to dashboard

### Test 3: Logout
1. Click "Logout" button
2. You should be redirected to login page

### Test 4: Admin Access
1. Login with admin credentials
2. You should see "Admin" option in navigation
3. Click to access admin dashboard

### Test 5: Protected Routes
1. Try accessing `/Dashboard` without logging in
2. You should be redirected to login

---

## Common First-Time Issues

### Issue: "Database is locked"
**Solution**: Close other instances of the app, or restart.

### Issue: Can't send emails
**Solution**: Check SMTP settings in `.env`. For Gmail, use App Password.

### Issue: App won't start
**Solution**: Make sure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Forgot admin password
**Solution**: Delete `chatbot_auth.db` and restart (removes all data):
```bash
rm chatbot_auth.db
streamlit run app.py
```

---

## Key Files Explained

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application |
| `config.py` | Configuration settings |
| `database.py` | Database models and operations |
| `auth_security.py` | Security functions (hashing, JWT, etc) |
| `validators.py` | Input validation |
| `.env` | Secret variables (don't commit!) |
| `requirements.txt` | Python dependencies |

---

## Security Checklist

Before going to production, verify:

- [ ] Changed default admin password
- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Configured email properly for password resets
- [ ] Set `DEBUG=False` in `.env`
- [ ] Using PostgreSQL (not SQLite)
- [ ] Enabled HTTPS on your domain
- [ ] Set up proper CORS settings
- [ ] Configured backup strategy
- [ ] Enabled rate limiting
- [ ] Set up monitoring/logging

---

## Connecting to Your Chatbot

### Option 1: Direct Integration
In your chatbot app, check for valid token:

```python
import requests

token = st.session_state.get('token')

if not token:
    st.error("Please login first")
    st.stop()

# Use token for API calls
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://api.example.com/chat", headers=headers)
```

### Option 2: Iframe Embedding
```html
<iframe 
    src="http://localhost:8501/?page=dashboard"
    width="100%"
    height="600px"
></iframe>
```

### Option 3: Separate Deployment
Deploy auth system separately:
```bash
streamlit run app.py --server.port=8501
# Chatbot runs on separate port
streamlit run chatbot.py --server.port=8502
```

---

## Performance Tips

### For Development
- SQLite is fine for testing
- DEBUG=True for detailed logs
- Single-threaded is OK

### For Production
- Use PostgreSQL with connection pooling
- Enable caching for user data
- Use Gunicorn/uWSGI for Python
- Set up reverse proxy (Nginx)
- Enable GZIP compression
- Use CDN for static files

---

## Monitoring & Maintenance

### Check System Health
```bash
# View app logs
tail -f app.log

# Check database size
ls -lh chatbot_auth.db

# View active sessions
sqlite3 chatbot_auth.db "SELECT COUNT(*) FROM sessions WHERE is_active=1;"
```

### Regular Maintenance
```bash
# Weekly: Clear expired sessions
sqlite3 chatbot_auth.db "DELETE FROM sessions WHERE expires_at < datetime('now');"

# Monthly: Clear old login attempts
sqlite3 chatbot_auth.db "DELETE FROM login_attempts WHERE attempt_time < datetime('now', '-30 days');"

# Monthly: Backup database
cp chatbot_auth.db chatbot_auth.db.backup.$(date +%Y%m%d)
```

---

## Getting Help

### Documentation
- See `IMPLEMENTATION_GUIDE.md` for detailed setup
- See `INTEGRATION_GUIDE.md` for API examples

### Common Questions

**Q: How do I add 2FA?**
A: Check roadmap in IMPLEMENTATION_GUIDE.md

**Q: Can I use social login (Google, GitHub)?**
A: Roadmap feature, not yet implemented

**Q: How many users can the system support?**
A: SQLite: ~1000 users, PostgreSQL: Unlimited

**Q: How do I reset the database?**
A: Delete `chatbot_auth.db` file and restart

**Q: Can I customize the UI?**
A: Yes! Edit `app.py` CSS section

---

## Next: Going Live

1. **Domain Setup**
   - Point domain to your server
   - Get SSL certificate (Let's Encrypt)
   - Configure DNS records

2. **Database Migration**
   - Set up PostgreSQL
   - Update `.env` with database URL
   - Verify connection

3. **Deployment**
   - Choose hosting (Streamlit Cloud, AWS, Heroku, etc.)
   - Set environment variables
   - Deploy application

4. **Post-Launch**
   - Monitor logs
   - Watch for errors
   - Set up backups
   - Enable monitoring alerts

---

## Useful Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install new package
pip install package-name

# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# View database contents
sqlite3 chatbot_auth.db
.tables                      # View tables
SELECT * FROM users;         # View users
.quit                        # Exit

# Clear cache
rm -rf .streamlit/
rm -rf __pycache__/

# Run tests
python -m pytest

# Format code
black .

# Check for issues
pylint *.py
```

---

## Success Checklist

After completing setup:

- [ ] App runs without errors
- [ ] Can create new account
- [ ] Can login with new account
- [ ] Can logout successfully
- [ ] Admin can access admin dashboard
- [ ] Regular users cannot access admin features
- [ ] Profile can be edited
- [ ] Password can be changed
- [ ] Rate limiting works (5 failed attempts lock account)
- [ ] Database stores all data correctly

---

**You're all set! 🎉 Your secure authentication system is ready to use.**

For detailed configuration and advanced features, see IMPLEMENTATION_GUIDE.md
