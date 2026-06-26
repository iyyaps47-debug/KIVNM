# 🌍 Production Deployment Guide

Complete guide for deploying the authentication system to production.

---

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Streamlit Cloud](#streamlit-cloud-deployment)
3. [AWS Deployment](#aws-elastic-beanstalk)
4. [Heroku Deployment](#heroku-deployment)
5. [Digital Ocean Deployment](#digital-ocean-deployment)
6. [Docker Deployment](#docker-deployment)
7. [Production Best Practices](#production-best-practices)
8. [Monitoring & Maintenance](#monitoring--maintenance)

---

## ✅ Pre-Deployment Checklist

### Security
- [ ] Changed default admin password
- [ ] Generated new SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Set `DEBUG=False` in .env
- [ ] Removed any hardcoded credentials
- [ ] Reviewed database schema
- [ ] Configured CORS properly
- [ ] Set up SSL/HTTPS certificates
- [ ] Enabled rate limiting
- [ ] Configured email for alerts

### Database
- [ ] Set up PostgreSQL (not SQLite)
- [ ] Tested database connection
- [ ] Created database backups
- [ ] Set up automated backups
- [ ] Verified connection pooling
- [ ] Added database indexes

### Configuration
- [ ] Created production .env file
- [ ] Configured email service
- [ ] Set up logging
- [ ] Configured CDN (if using)
- [ ] Set up monitoring alerts

### Code
- [ ] Ran all tests
- [ ] Removed debug code
- [ ] Updated documentation
- [ ] Tested all features
- [ ] Performance tested
- [ ] Security audited

### Infrastructure
- [ ] Domain configured
- [ ] SSL certificate installed
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Load balancer configured
- [ ] Caching configured

---

## 🚀 Streamlit Cloud Deployment

### Step 1: Prepare GitHub Repository

```bash
# Initialize git
git init
git add .
git commit -m "Initial commit: Authentication system"

# Add to GitHub
git remote add origin https://github.com/yourusername/repo.git
git push -u origin main
```

### Step 2: Create Streamlit App

1. Go to https://share.streamlit.io
2. Click "New app"
3. Connect GitHub account
4. Select your repository
5. Choose branch: `main`
6. Set main file: `app.py`
7. Click "Deploy"

### Step 3: Configure Secrets

1. Click "..." → "Settings"
2. Go to "Secrets"
3. Add secrets:

```toml
[secrets]
SECRET_KEY = "your-generated-secret-key"
DB_TYPE = "sqlite"
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
DEBUG = "False"
```

### Step 4: Monitor Deployment

```bash
# Watch the logs during deployment
# Click "Manage app" to view
```

### Streamlit Cloud Limitations

- SQLite files are temporary (reset on rerun)
- Solution: Use managed database service
- Storage: Limited to app cache

### Solution: Use Managed Database

```python
# In config.py, use cloud database
import os

if os.environ.get('STREAMLIT_DEPLOYMENT'):
    # Cloud deployment - use managed database
    DATABASE_URL = os.getenv('DATABASE_URL')  # Provided by Streamlit
else:
    # Local development
    DATABASE_URL = "sqlite:///chatbot_auth.db"
```

---

## ☁️ AWS Elastic Beanstalk

### Step 1: Prepare Application

```bash
# Create requirements.txt (already done)
# Create Procfile
echo "web: streamlit run app.py --server.port=8000" > Procfile

# Create .ebextensions/python.config
mkdir -p .ebextensions
cat > .ebextensions/python.config << 'EOF'
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
  aws:elasticbeanstalk:application:environment:
    PYTHONUNBUFFERED: true
EOF
```

### Step 2: Install EB CLI

```bash
pip install awsebcli
```

### Step 3: Create EB Application

```bash
# Initialize
eb init -p python-3.9 chatbot-auth --region us-east-1

# Create environment
eb create chatbot-auth-prod

# Deploy
eb deploy

# Open in browser
eb open
```

### Step 4: Configure Environment Variables

```bash
# Set secrets in AWS Systems Manager Parameter Store
aws ssm put-parameter \
    --name /chatbot-auth/SECRET_KEY \
    --value "your-secret-key" \
    --type SecureString \
    --region us-east-1

# Reference in .ebextensions/python.config
option_settings:
  aws:autoscaling:launchconfiguration:
    EnvironmentVariables:
      SECRET_KEY: /chatbot-auth/SECRET_KEY
```

### Step 5: Set Up RDS Database

```bash
# Create PostgreSQL RDS instance
aws rds create-db-instance \
    --db-instance-identifier chatbot-auth-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password <password> \
    --allocated-storage 20

# Get endpoint and update DATABASE_URL
aws rds describe-db-instances --db-instance-identifier chatbot-auth-db
```

---

## 🍃 Heroku Deployment

### Step 1: Install Heroku CLI

```bash
# macOS
brew install heroku/brew/heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Create Procfile

```bash
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
```

### Step 3: Deploy to Heroku

```bash
# Login
heroku login

# Create app
heroku create chatbot-auth-prod

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set DATABASE_URL=postgresql://...

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Step 4: Add PostgreSQL

```bash
# Add free tier
heroku addons:create heroku-postgresql:hobby-dev

# Get connection string
heroku config | grep DATABASE_URL

# Update config.py to use it
```

---

## 💧 Digital Ocean Deployment

### Step 1: Create Droplet

```bash
# Via CLI
doctl compute droplet create chatbot-auth \
    --region nyc3 \
    --image ubuntu-22-04-x64 \
    --size s-1vcpu-1gb

# Via Web Console
# Select: Ubuntu 22.04
# Size: $5/month (1GB RAM, 25GB SSD)
# Region: Nearest to you
```

### Step 2: Install Dependencies

```bash
# SSH into droplet
ssh root@your_droplet_ip

# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install -y python3.9 python3-pip python3-venv
apt install -y postgresql postgresql-contrib nginx

# Clone repository
git clone https://github.com/yourusername/repo.git
cd repo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### Step 3: Set Up PostgreSQL

```bash
# Start PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres createdb chatbot_auth
sudo -u postgres psql << EOF
CREATE USER chatbot_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE chatbot_auth TO chatbot_user;
EOF
```

### Step 4: Configure Nginx

```bash
# Create Nginx config
cat > /etc/nginx/sites-available/chatbot-auth << 'EOF'
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
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

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/chatbot-auth /etc/nginx/sites-enabled/
nginx -s reload
```

### Step 5: Get SSL Certificate

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get certificate
certbot certonly --standalone -d yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

### Step 6: Create Systemd Service

```bash
# Create service file
cat > /etc/systemd/system/chatbot-auth.service << 'EOF'
[Unit]
Description=Chatbot Auth Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/repo
Environment="PATH=/root/repo/venv/bin"
ExecStart=/root/repo/venv/bin/streamlit run app.py \
    --server.port=8501 \
    --server.address=localhost \
    --logger.level=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable chatbot-auth
systemctl start chatbot-auth

# Check status
systemctl status chatbot-auth
```

---

## 🐳 Docker Deployment

### Step 1: Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user
RUN useradd -m streamlit
USER streamlit

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--logger.level=info"]
```

### Step 2: Create Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/chatbot_auth
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
    depends_on:
      - db
    volumes:
      - ./chatbot_auth.db:/app/chatbot_auth.db
    restart: always

  db:
    image: postgres:14-alpine
    environment:
      - POSTGRES_USER=chatbot_user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=chatbot_auth
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

### Step 3: Build and Run

```bash
# Build
docker build -t chatbot-auth .

# Run
docker run -p 8501:8501 chatbot-auth

# Or with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop
docker-compose down
```

---

## 📊 Production Best Practices

### 1. Database Optimization

```python
# Add connection pooling for PostgreSQL
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

### 2. Caching Strategy

```python
# Cache database queries
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@st.cache_resource
def get_users():
    # Cache for 1 hour
    cached = redis_client.get('all_users')
    if cached:
        return json.loads(cached)
    
    users = db.get_all_users()
    redis_client.setex('all_users', 3600, json.dumps([u.to_dict() for u in users]))
    return users
```

### 3. Rate Limiting

```python
# Use Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per 15 minutes")
def login():
    # Login logic
    pass
```

### 4. Security Headers

```python
# Add security headers
@app.after_request
def set_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

### 5. Logging & Monitoring

```python
# Configure structured logging
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module
        }
        return json.dumps(log_obj)

handler = logging.FileHandler('app.log')
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

### 6. Backup Strategy

```bash
#!/bin/bash
# backup.sh - Daily backup script

BACKUP_DIR="/backups"
DB_NAME="chatbot_auth"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL
pg_dump $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Compress
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql.gz s3://your-bucket/backups/

# Keep only 30 days of backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed at $(date)"
```

---

## 👀 Monitoring & Maintenance

### 1. Health Checks

```python
@app.route('/health', methods=['GET'])
def health():
    try:
        # Check database
        db.get_all_users()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

### 2. Monitoring Tools

Recommended:
- **Application Monitoring**: New Relic, Datadog
- **Database Monitoring**: pgAdmin, Adminer
- **Error Tracking**: Sentry, Rollbar
- **Logging**: ELK Stack, Splunk, CloudWatch
- **Uptime Monitoring**: Pingdom, UptimeRobot

### 3. Alerts

Set up alerts for:
- Failed login attempts > 50 per hour
- Database connection errors
- Server downtime
- High memory usage
- High CPU usage
- Slow query detection

### 4. Regular Maintenance

```bash
# Weekly
- Review logs for errors
- Check database size
- Verify backups

# Monthly
- Clear expired sessions
- Clear old login attempts
- Analyze slow queries
- Update dependencies

# Quarterly
- Security audit
- Performance review
- Disaster recovery test
```

---

## 📈 Performance Tuning

### Database Indexes

```sql
-- Add indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_login_attempts_email ON login_attempts(email);
CREATE INDEX idx_login_attempts_attempt_time ON login_attempts(attempt_time);
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp);
```

### Query Optimization

```python
# Use LIMIT to prevent large result sets
def get_user_activity(user_id, limit=100):
    cursor.execute('''
        SELECT * FROM chat_history 
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))

# Use SELECT only needed columns
cursor.execute('''
    SELECT id, name, email FROM users
    WHERE role = ?
''', ('user',))
```

---

## 🔐 Production Security Checklist

```
[ ] All .env variables set
[ ] DEBUG = False
[ ] Secret key is strong and random
[ ] Database password is strong
[ ] HTTPS/SSL configured
[ ] CORS whitelist configured
[ ] Rate limiting enabled
[ ] Database backup automated
[ ] Monitoring configured
[ ] Alerting configured
[ ] Admin password changed
[ ] Log files secured
[ ] Database encrypted
[ ] Backups encrypted
[ ] Regular security updates
[ ] Secrets management configured
```

---

**Choose your deployment platform above and follow the step-by-step guide. For questions, refer to the main documentation files.**
