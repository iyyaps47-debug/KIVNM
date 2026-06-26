import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# ============ APPLICATION SETTINGS ============
APP_NAME = "LearnMate - Secure Auth System"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False") == "True"

# ============ STREAMLIT SETTINGS ============
STREAMLIT_CONFIG = {
    "theme.primaryColor": "#FF6B9D",
    "theme.backgroundColor": "#FFF0F3",
    "theme.secondaryBackgroundColor": "#FCE4EC",
    "theme.textColor": "#262730",
    "theme.font": "sans serif",
}

# ============ DATABASE SETTINGS ============
# SQLite for development (change to PostgreSQL for production)
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_PATH = os.getenv("DB_PATH", "chatbot_auth.db")

if DB_TYPE == "sqlite":
    DATABASE_URL = f"sqlite:///{DB_PATH}"
else:
    # PostgreSQL
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "chatbot_auth")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ============ JWT SETTINGS ============
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ============ PASSWORD SETTINGS ============
MIN_PASSWORD_LENGTH = 8
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_DIGITS = True
REQUIRE_SPECIAL_CHARS = True

# ============ SECURITY SETTINGS ============
BCRYPT_LOG_ROUNDS = 12
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
RATE_LIMIT_ENABLED = True

# ============ EMAIL SETTINGS ============
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "smtp")  # gmail, sendgrid, smtp
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@skillzlearn.com")
FROM_NAME = "SkillzLearn Support"

# ============ FRONTEND SETTINGS ============
LOGIN_REDIRECT_URL = "/Dashboard"
LOGOUT_REDIRECT_URL = "/"
ADMIN_DASHBOARD_URL = "/Admin"

# ============ SESSION SETTINGS ============
SESSION_TIMEOUT_MINUTES = 60
REMEMBER_ME_DAYS = 30

# ============ CHATBOT SETTINGS ============
CHATBOT_API_URL = "https://kinvcreation4655.streamlit.app"
CHATBOT_REQUIRE_AUTH = True

# ============ CORS SETTINGS ============
CORS_ORIGINS = [
    "http://localhost:8501",
    "http://localhost:3000",
    "https://kinvcreation4655.streamlit.app",
    "*"  # Allow all in development, restrict in production
]

# ============ ADMIN SETTINGS ============
ADMIN_ROLES = ["admin", "superadmin"]
DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@skillzlearn.com")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "AdminPassword123!")

# ============ FEATURE FLAGS ============
ENABLE_SOCIAL_LOGIN = False
ENABLE_2FA = False
ENABLE_EMAIL_VERIFICATION = True
ENABLE_PASSWORD_RESET = True

# ============ LOGGING SETTINGS ============
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "app.log"
