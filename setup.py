#!/usr/bin/env python3
"""
Setup script for SkillzLearn Authentication System
Initializes database, creates admin account, and configures environment
"""

import os
import sys
import secrets
import json
from pathlib import Path
from database import db
from auth_security import PasswordManager
from validators import EmailValidator, PasswordValidator


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_error(f"Python 3.9+ required. You have {version.major}.{version.minor}")
        sys.exit(1)
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} is compatible")


def check_dependencies():
    """Check if all required packages are installed"""
    print_header("Checking Dependencies")
    
    required_packages = [
        'streamlit',
        'bcrypt',
        'jwt',
        'email_validator',
        'cryptography'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"Found {package}")
        except ImportError:
            print_error(f"Missing {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print_error(f"\nMissing packages: {', '.join(missing_packages)}")
        print_info("Install with: pip install -r requirements.txt")
        sys.exit(1)
    
    print_success("All dependencies installed")


def initialize_database():
    """Initialize database"""
    print_header("Initializing Database")
    
    print_info("Creating database tables...")
    
    try:
        # Database will be initialized automatically
        from database import db
        print_success("Database initialized successfully")
        
        # Check if any users exist
        existing_users = db.get_all_users()
        print_info(f"Current users in database: {len(existing_users)}")
        
    except Exception as e:
        print_error(f"Failed to initialize database: {e}")
        sys.exit(1)


def create_admin_account():
    """Create default admin account"""
    print_header("Creating Admin Account")
    
    # Check if admin already exists
    admin = db.get_user_by_email("admin@skillzlearn.com")
    
    if admin:
        print_info("Admin account already exists")
        
        response = input("Do you want to create a new admin account? (y/n): ")
        if response.lower() != 'y':
            return
    
    while True:
        admin_email = input("Enter admin email (default: admin@skillzlearn.com): ").strip()
        if not admin_email:
            admin_email = "admin@skillzlearn.com"
        
        # Validate email
        is_valid, message = EmailValidator.validate(admin_email)
        if not is_valid:
            print_error(f"Invalid email: {message}")
            continue
        
        # Check if email exists
        existing_user = db.get_user_by_email(admin_email)
        if existing_user:
            print_error("Email already registered")
            continue
        
        break
    
    while True:
        admin_password = input("Enter admin password (min 8 chars, uppercase, lowercase, digit, special char): ").strip()
        
        # Validate password
        is_valid, errors = PasswordValidator.validate(admin_password)
        if not is_valid:
            print_error("Invalid password:")
            for error in errors:
                print(f"  - {error}")
            continue
        
        confirm_password = input("Confirm admin password: ").strip()
        
        if admin_password != confirm_password:
            print_error("Passwords do not match")
            continue
        
        break
    
    admin_name = input("Enter admin name (default: Admin): ").strip()
    if not admin_name:
        admin_name = "Admin"
    
    # Create admin user
    try:
        admin_user = db.create_user(admin_name, admin_email, admin_password, role="admin")
        
        if admin_user:
            print_success(f"Admin account created: {admin_email}")
        else:
            print_error("Failed to create admin account")
    
    except Exception as e:
        print_error(f"Error creating admin account: {e}")


def setup_environment_file():
    """Setup .env file"""
    print_header("Configuring Environment Variables")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print_info(".env file already exists")
        response = input("Do you want to update it? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Generate secret key
    secret_key = secrets.token_urlsafe(32)
    
    # Default config
    env_config = f"""
# ============ APPLICATION SETTINGS ============
APP_NAME=LearnMate - Secure Auth System
DEBUG=False

# ============ DATABASE SETTINGS ============
DB_TYPE=sqlite
DB_PATH=chatbot_auth.db

# ============ SECURITY SETTINGS ============
SECRET_KEY={secret_key}
ALGORITHM=HS256
BCRYPT_LOG_ROUNDS=12

# ============ PASSWORD SETTINGS ============
MIN_PASSWORD_LENGTH=8
REQUIRE_UPPERCASE=True
REQUIRE_LOWERCASE=True
REQUIRE_DIGITS=True
REQUIRE_SPECIAL_CHARS=True

# ============ RATE LIMITING ============
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
RATE_LIMIT_ENABLED=True

# ============ JWT SETTINGS ============
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SESSION_TIMEOUT_MINUTES=60
REMEMBER_ME_DAYS=30

# ============ EMAIL SETTINGS ============
# Leave empty to disable email features
EMAIL_PROVIDER=smtp
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
FROM_EMAIL=noreply@skillzlearn.com

# ============ FEATURE FLAGS ============
ENABLE_EMAIL_VERIFICATION=True
ENABLE_PASSWORD_RESET=True
ENABLE_SOCIAL_LOGIN=False
ENABLE_2FA=False

# ============ LOGGING ============
LOG_LEVEL=INFO
LOG_FILE=app.log
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_config.strip())
        
        print_success(".env file created with default configuration")
        print_info(f"Secret Key (save securely): {secret_key}")
        print_info("Edit .env to configure email settings for password reset")
        
    except Exception as e:
        print_error(f"Failed to create .env file: {e}")


def create_requirements_file():
    """Create requirements.txt if it doesn't exist"""
    print_header("Checking Requirements File")
    
    requirements_file = Path("requirements.txt")
    
    if requirements_file.exists():
        print_info("requirements.txt already exists")
        return
    
    requirements = """streamlit==1.28.1
streamlit-authenticator==0.2.3
streamlit-extras==0.3.5
python-dotenv==1.0.0
PyJWT==2.8.1
bcrypt==4.1.1
email-validator==2.1.0
sqlalchemy==2.0.23
python-jose==3.3.0
passlib==1.7.4
cryptography==41.0.7
requests==2.31.0
pandas==2.1.3
plotly==5.18.0
"""
    
    try:
        with open(requirements_file, 'w') as f:
            f.write(requirements)
        
        print_success("requirements.txt created")
        print_info("Install with: pip install -r requirements.txt")
        
    except Exception as e:
        print_error(f"Failed to create requirements.txt: {e}")


def test_database_connection():
    """Test database connection"""
    print_header("Testing Database Connection")
    
    try:
        users = db.get_all_users()
        print_success(f"Database connection successful")
        print_info(f"Total users: {len(users)}")
        
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        sys.exit(1)


def display_summary():
    """Display setup summary"""
    print_header("Setup Complete! 🎉")
    
    print("\n📋 System Summary:")
    print("-" * 60)
    
    users = db.get_all_users()
    admins = [u for u in users if u.role in ['admin', 'superadmin']]
    
    print(f"Total Users:        {len(users)}")
    print(f"Admin Accounts:     {len(admins)}")
    print(f"Database Location:  chatbot_auth.db")
    print(f"Configuration:      .env")
    
    print("\n🚀 Next Steps:")
    print("-" * 60)
    print("1. Run the application:")
    print("   streamlit run app.py")
    print("\n2. Open your browser to: http://localhost:8501")
    print("\n3. Login with admin credentials")
    print("\n4. Customize settings in .env as needed")
    print("\n5. See IMPLEMENTATION_GUIDE.md for advanced setup")
    print("\n" + "=" * 60 + "\n")


def run_setup():
    """Run complete setup"""
    print("\n" + "=" * 60)
    print("  🔐 SkillzLearn Authentication System Setup")
    print("=" * 60 + "\n")
    
    try:
        check_python_version()
        check_dependencies()
        setup_environment_file()
        create_requirements_file()
        initialize_database()
        test_database_connection()
        create_admin_account()
        display_summary()
        
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_setup()
