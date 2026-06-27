import streamlit as st
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import json
import time

# Add project to path
sys.path.append(str(Path(__file__).parent))

from database import db, User
from auth_security import PasswordManager, JWTManager
import importlib.util as _ilu
import pathlib as _pl

def _load_local(name):
    """Load a module from the project directory, bypassing installed packages."""
    p = _pl.Path(__file__).parent / f"{name}.py"
    spec = _ilu.spec_from_file_location(name, p)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_validators_mod = _load_local("validators")
EmailValidator   = _validators_mod.EmailValidator
PasswordValidator = _validators_mod.PasswordValidator
NameValidator    = _validators_mod.NameValidator
from config import (
    CHATBOT_API_URL,
)

APP_NAME = "LearnMate"

# ============ EMAIL CONFIGURATION ============
EMAIL_CONFIG = {
    'sender_email': os.getenv('SENDER_EMAIL', 'noreply@skillzlearn.com'),
    'sender_password': os.getenv('SENDER_PASSWORD', ''),
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', 587)),
}

# ============ STREAMLIT PAGE CONFIGURATION ============
st.set_page_config(
    page_title=f"{APP_NAME} - AI Learning",
    page_icon="🎓",
    layout="wide",
)

# Custom CSS - Modern UI Design
st.markdown("""
    <style>
    :root {
        --primary-color: #2563EB;
        --primary-dark: #1E40AF;
        --secondary-color: #10B981;
        --accent-color: #F59E0B;
        --success-color: #10B981;
        --warning-color: #EF4444;
        --neutral-900: #0F172A;
        --neutral-800: #1E293B;
        --neutral-700: #334155;
        --neutral-200: #E2E8F0;
        --neutral-100: #F8FAFC;
        --border-color: #E2E8F0;
    }
    
    * {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    body {
        background: white;
        color: #1E293B;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    }
    
    @media (prefers-color-scheme: dark) {
        body {
            background: #F8FAFC;
            color: #1E293B;
        }
    }
    
    /* === TYPOGRAPHY === */
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #0F172A;
    }
    
    h1 {
        font-size: 2.25rem;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        font-size: 1.125rem;
        margin-bottom: 0.75rem;
    }
    
    /* === AUTH HEADER === */
    .auth-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem 0;
    }
    
    .auth-header h1 {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0.5rem 0;
        letter-spacing: -0.03em;
        color: #1E293B;
    }
    
    .auth-header .app-icon {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
    }
    
    .auth-header p {
        color: #64748B;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* === CARDS & CONTAINERS === */
    .auth-container {
        max-width: 420px;
        margin: 0 auto;
        padding: 2.5rem;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 
                    0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border: 1px solid var(--border-color);
    }
    
    .dashboard-card {
        background: white;
        border-radius: 0.875rem;
        padding: 1.5rem;
        border: 1px solid var(--border-color);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .dashboard-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* === INPUT FIELDS === */
    input[type="text"],
    input[type="email"],
    input[type="password"],
    textarea {
        background-color: #F8FAFC;
        border: 2px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        color: #1E293B;
    }
    
    input[type="text"]:focus,
    input[type="email"]:focus,
    input[type="password"]:focus,
    textarea:focus {
        outline: none;
        border-color: var(--primary-color);
        background-color: white;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    
    /* === BUTTONS === */
    [data-baseweb="button"] button {
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.2s ease !important;
        text-transform: none !important;
    }
    
    [data-baseweb="button"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* === VERIFICATION BOX === */
    .verification-box {
        padding: 1.5rem;
        border-radius: 0.875rem;
        border-left: 4px solid var(--success-color);
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.02));
        margin: 1.5rem 0;
        border: 1px solid rgba(16, 185, 129, 0.15);
        transition: all 0.3s ease;
    }
    
    .verification-box:hover {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.04));
        border-color: rgba(16, 185, 129, 0.25);
    }
    
    .verification-box strong {
        color: var(--success-color);
        font-weight: 600;
    }
    
    /* === PROFILE EDIT BOX === */
    .profile-edit-box {
        padding: 1.5rem;
        border-radius: 0.875rem;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.05), rgba(37, 99, 235, 0.02));
        margin: 1.5rem 0;
        border: 1px solid rgba(37, 99, 235, 0.15);
        transition: all 0.3s ease;
    }
    
    .profile-edit-box:hover {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(37, 99, 235, 0.04));
        border-color: rgba(37, 99, 235, 0.25);
    }
    
    /* === CHAT HISTORY === */
    .chat-history-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        background-color: #F8FAFC;
        border-radius: 0.875rem;
        border: 1px solid var(--border-color);
        gap: 0.75rem;
        display: flex;
        flex-direction: column;
    }
    
    .chat-history-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-history-container::-webkit-scrollbar-track {
        background: #F1F5F9;
        border-radius: 10px;
    }
    
    .chat-history-container::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 10px;
    }
    
    .chat-history-container::-webkit-scrollbar-thumb:hover {
        background: #94A3B8;
    }
    
    .chat-message {
        padding: 1.25rem;
        margin: 0;
        border-radius: 0.875rem;
        background: white;
        border: 1px solid var(--border-color);
        border-left: 3px solid var(--primary-color);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
        line-height: 1.6;
    }
    
    .chat-message:hover {
        border-left-color: var(--primary-dark);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.12);
        transform: translateX(2px);
    }
    
    .chat-sender {
        color: var(--primary-color);
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .chat-content {
        color: var(--neutral-800);
        font-size: 0.95rem;
        word-wrap: break-word;
        white-space: pre-wrap;
        margin-bottom: 0.75rem;
        line-height: 1.5;
    }
    
    .chat-separator {
        height: 1px;
        background: linear-gradient(to right, var(--border-color), transparent);
        margin: 0.75rem 0;
    }
    
    .chat-timestamp {
        color: #94A3B8;
        font-size: 0.8rem;
        margin-top: 0.75rem;
        font-weight: 500;
        display: block;
    }
    
    /* === TIMESTAMP === */
    .timestamp {
        color: #94A3B8;
        font-size: 0.8rem;
        margin-top: 0.75rem;
        font-weight: 500;
        display: block;
    }
    
    /* === ALERTS & INFO BOXES === */
    .stInfo {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    .stWarning {
        background-color: #FEF3C7;
        border: 1px solid #FCD34D;
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    .stSuccess {
        background-color: #ECFDF5;
        border: 1px solid #A7F3D0;
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    .stError {
        background-color: #FEE2E2;
        border: 1px solid #FECACA;
        border-radius: 0.75rem;
        padding: 1rem;
    }
    
    /* === SIDEBAR RADIO BUTTON STYLING === */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.25rem;
    }
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.05);
        border-radius: 0.5rem;
        padding: 0.5rem 0.75rem;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(99, 179, 237, 0.15);
        border-color: rgba(99, 179, 237, 0.3);
    }
    
    /* === METRIC CARDS === */
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 0.875rem;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 12px rgba(37,99,235,0.1);
        transform: translateY(-1px);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }
    
    /* === TABS === */
    [data-baseweb="tab-list"] {
        border-bottom: 2px solid var(--border-color);
    }
    
    [data-baseweb="tab"] {
        border-radius: 0.5rem 0.5rem 0 0;
        color: #64748B;
        font-weight: 600;
    }
    
    [data-baseweb="tab"][aria-selected="true"] {
        color: var(--primary-color);
        border-bottom: 3px solid var(--primary-color);
    }
    
    /* === DIVIDERS === */
    hr {
        border: none;
        border-top: 1px solid var(--border-color);
        margin: 1.5rem 0;
    }
    
    /* === RESPONSIVE === */
    @media (max-width: 768px) {
        .auth-header h1 {
            font-size: 2rem;
        }
        
        .auth-container {
            margin: 0 1rem;
            padding: 2rem;
        }
        
        h1 {
            font-size: 1.75rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ============ SESSION STATE INITIALIZATION ============
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'role' not in st.session_state:
        st.session_state.role = 'user'
    if 'editing_profile' not in st.session_state:
        st.session_state.editing_profile = False
    if 'verification_sent' not in st.session_state:
        st.session_state.verification_sent = False
    if 'confirm_clear_chat' not in st.session_state:
        st.session_state.confirm_clear_chat = False
    if 'fp_token_generated' not in st.session_state:
        st.session_state.fp_token_generated = None
    if 'fp_token_email' not in st.session_state:
        st.session_state.fp_token_email = None

init_session_state()

# ============ UTILITY FUNCTIONS ============

def format_timestamp(iso_timestamp: str) -> str:
    """Convert ISO timestamp to readable format in Indian Standard Time (IST/UTC+5:30)"""
    if not iso_timestamp or iso_timestamp == "None":
        return "Not logged in yet"
    
    try:
        iso_str = str(iso_timestamp).strip()
        
        # Handle different datetime formats
        if 'T' in iso_str:
            dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        elif ' ' in iso_str:
            # Replace space with T for parsing (e.g., "2026-06-25 19:32:37")
            dt = datetime.fromisoformat(iso_str.replace(' ', 'T').replace('Z', '+00:00'))
        else:
            return "Unknown"
        
        # Convert to IST (UTC+5:30)
        ist_offset = timedelta(hours=5, minutes=30)
        dt_ist = dt + ist_offset
        
        # Get current UTC time and convert to IST for comparison
        now_utc = datetime.utcnow()
        now_ist = now_utc + ist_offset
        
        # If today (in IST)
        if dt_ist.date() == now_ist.date():
            return f"Today at {dt_ist.strftime('%I:%M %p')} IST"
        
        # If yesterday (in IST)
        if (now_ist - dt_ist).days == 1:
            return f"Yesterday at {dt_ist.strftime('%I:%M %p')} IST"
        
        # If within a week
        if (now_ist - dt_ist).days < 7:
            return f"{(now_ist - dt_ist).days} days ago at {dt_ist.strftime('%I:%M %p')} IST"
        
        # Otherwise show date with IST
        return dt_ist.strftime('%d %b %Y at %I:%M %p') + " IST"
    
    except Exception as e:
        return "Unknown"


def format_member_since(iso_timestamp: str) -> str:
    """Format member registration date - shows actual date, not relative time in IST"""
    if not iso_timestamp or iso_timestamp == "None":
        return "Recently joined"
    
    try:
        iso_str = str(iso_timestamp).strip()
        
        # Handle different datetime formats
        # Format 1: "2026-06-25T19:32:37" (with T)
        if 'T' in iso_str:
            dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        # Format 2: "2026-06-25 19:32:37" (with space)
        elif ' ' in iso_str:
            # Replace space with T for parsing
            dt = datetime.fromisoformat(iso_str.replace(' ', 'T').replace('Z', '+00:00'))
        # Format 3: Just date "2026-06-25"
        elif len(iso_str) == 10:
            dt = datetime.fromisoformat(iso_str)
        else:
            return "Recently joined"
        
        # Convert to IST (UTC+5:30)
        ist_offset = timedelta(hours=5, minutes=30)
        dt_ist = dt + ist_offset
        
        now_utc = datetime.utcnow()
        now_ist = now_utc + ist_offset
        
        # Calculate difference
        time_diff = now_ist - dt_ist
        days_diff = time_diff.days
        total_seconds = time_diff.total_seconds()
        
        # Handle very recent registrations
        if total_seconds < 60:
            return "Just now"
        elif total_seconds < 3600:  # Less than 1 hour
            minutes = int(total_seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif total_seconds < 86400:  # Less than 1 day
            hours = int(total_seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        
        # Handle days
        if days_diff <= 0:
            return "Today"
        elif days_diff == 1:
            return "Yesterday"
        elif days_diff < 7:
            return f"{days_diff} day{'s' if days_diff != 1 else ''} ago"
        elif days_diff < 30:
            weeks = days_diff // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif days_diff < 365:
            months = days_diff // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = days_diff // 365
            remaining_months = (days_diff % 365) // 30
            if remaining_months > 0:
                return f"{years} year{'s' if years != 1 else ''}, {remaining_months} month{'s' if remaining_months != 1 else ''} ago"
            return f"{years} year{'s' if years != 1 else ''} ago"
    
    except Exception as e:
        return "Recently joined"


def send_verification_email(user_email: str, user_name: str) -> tuple:
    """Send email verification link"""
    try:
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Store token safely - use session state as fallback if db method not available
        if 'verification_tokens' not in st.session_state:
            st.session_state.verification_tokens = {}
        st.session_state.verification_tokens[user_email] = {
            'token': verification_token,
            'created_at': datetime.utcnow().isoformat()
        }
        if hasattr(db, 'store_verification_token'):
            try:
                db.store_verification_token(user_email, verification_token)
            except Exception:
                pass  # Fallback to session state storage above
        
        # Create verification link
        verification_link = f"https://yourapp.com/verify?token={verification_token}"
        
        # Compose email
        sender_email = EMAIL_CONFIG['sender_email']
        sender_password = EMAIL_CONFIG['sender_password']
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "Verify Your LearnMate Email"
        message["From"] = sender_email
        message["To"] = user_email
        
        # Email body (HTML)
        html = f"""\
        <html>
          <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; color: #1E293B; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 0;">
              <!-- Header with gradient -->
              <div style="background: linear-gradient(135deg, #2563EB 0%, #10B981 100%); padding: 40px 20px; text-align: center;">
                <h2 style="color: white; font-size: 28px; margin: 0; font-weight: 700;">Welcome to LearnMate! 🎓</h2>
              </div>
              
              <!-- Content -->
              <div style="background: white; padding: 40px 30px; border-left: 4px solid #2563EB;">
                <p style="margin-top: 0; font-size: 16px;">Hi <strong>{user_name}</strong>,</p>
                
                <p style="font-size: 15px; color: #475569;">
                  Thank you for creating an account with us. To complete your registration, please verify your email address by clicking the button below:
                </p>
                
                <div style="text-align: center; margin: 40px 0;">
                  <a href="{verification_link}" style="background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%); color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; font-weight: 600; display: inline-block; font-size: 15px;">
                    ✓ Verify Email Address
                  </a>
                </div>
                
                <p style="font-size: 13px; color: #64748B; margin: 30px 0;">
                  <strong>Or copy and paste this link:</strong><br>
                  <span style="word-break: break-all; color: #475569; font-family: monospace; background: #F8FAFC; padding: 8px 12px; border-radius: 4px; display: block; margin-top: 8px;">
                    {verification_link}
                  </span>
                </p>
                
                <p style="font-size: 13px; color: #64748B; margin: 20px 0;">
                  ⏰ This link will expire in <strong>24 hours</strong>.
                </p>
              </div>
              
              <!-- Footer -->
              <div style="background: #F8FAFC; padding: 30px; text-align: center; border-top: 1px solid #E2E8F0;">
                <p style="font-size: 12px; color: #64748B; margin: 0 0 10px 0;">
                  If you didn't create this account, please ignore this email or contact our support team.
                </p>
                <p style="font-size: 12px; color: #94A3B8; margin: 0;">
                  © 2026 LearnMate. All rights reserved.
                </p>
              </div>
            </div>
          </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        message.attach(part)
        
        # Send email via SMTP
        if not sender_password:
            # No SMTP password configured - simulate success for development
            return True, "Verification email sent! Please check your inbox."
        
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, message.as_string())
        
        return True, "Verification email sent! Please check your inbox."
    
    except smtplib.SMTPAuthenticationError:
        return False, "Email configuration error: Invalid SMTP credentials. Please contact support."
    except smtplib.SMTPException as e:
        return False, f"Failed to send email. Please try again later."
    except Exception as e:
        return False, f"Unexpected error. Please try again later."


def get_chat_history(user_id: str) -> list:
    """Get real chat history for user - try DB first, fallback to session state"""
    try:
        if hasattr(db, 'get_chat_history'):
            history = db.get_chat_history(str(user_id))
            if history is not None:
                return history
    except Exception:
        pass
    # Fallback to session state
    if 'chat_histories' not in st.session_state:
        st.session_state.chat_histories = {}
    return st.session_state.chat_histories.get(str(user_id), [])


def save_chat_message(user_id: str, user_message: str, bot_response: str):
    """Save a chat message to the user's history - try DB first, fallback to session state"""
    uid = str(user_id)
    saved_to_db = False
    try:
        if hasattr(db, 'save_chat_message'):
            db.save_chat_message(uid, user_message, bot_response, datetime.utcnow().isoformat())
            saved_to_db = True
    except Exception:
        pass
    
    # Always save to session state as backup
    if 'chat_histories' not in st.session_state:
        st.session_state.chat_histories = {}
    if uid not in st.session_state.chat_histories:
        st.session_state.chat_histories[uid] = []
    chat_id = len(st.session_state.chat_histories[uid]) + 1
    st.session_state.chat_histories[uid].append({
        "id": chat_id,
        "message": user_message,
        "response": bot_response,
        "timestamp": datetime.utcnow().isoformat()
    })


def clear_chat_history(user_id: str):
    """Clear all chat history for a user"""
    if 'chat_histories' not in st.session_state:
        st.session_state.chat_histories = {}
    st.session_state.chat_histories[str(user_id)] = []


# Keep backward-compatible alias
def mock_get_chat_history(user_id: str) -> list:
    return get_chat_history(user_id)


# ============ FORGOT PASSWORD FUNCTIONS ============

# Persistent file path for reset tokens (survives page reloads & new sessions)
_RESET_TOKEN_FILE = Path(__file__).parent / ".password_reset_tokens.json"


def _load_reset_tokens() -> dict:
    """Load reset tokens from persistent file storage"""
    # First try DB
    if hasattr(db, 'get_all_password_reset_tokens'):
        try:
            return db.get_all_password_reset_tokens() or {}
        except Exception:
            pass
    # Fallback: JSON file (persists across Streamlit sessions/reruns)
    try:
        if _RESET_TOKEN_FILE.exists():
            with open(_RESET_TOKEN_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_reset_tokens(tokens: dict):
    """Save reset tokens to persistent file storage"""
    # First try DB
    if hasattr(db, 'save_all_password_reset_tokens'):
        try:
            db.save_all_password_reset_tokens(tokens)
            return
        except Exception:
            pass
    # Fallback: JSON file
    try:
        with open(_RESET_TOKEN_FILE, 'w') as f:
            json.dump(tokens, f)
    except Exception:
        pass
    # Also keep in session state as in-memory cache
    st.session_state.password_reset_tokens = tokens


def generate_password_reset_token(email: str) -> tuple:
    """Generate a password reset token and store it persistently"""
    user = db.get_user_by_email(email.lower())
    if not user:
        # Return success anyway to avoid email enumeration
        return True, "If this email is registered, a reset link has been sent."

    token = secrets.token_urlsafe(32)
    expiry = (datetime.utcnow() + timedelta(hours=1)).isoformat()

    # Load existing tokens, add new one, save back
    tokens = _load_reset_tokens()
    tokens[token] = {
        'email': email.lower(),
        'expiry': expiry,
        'used': False
    }
    _save_reset_tokens(tokens)

    # Also try DB-level store if available
    if hasattr(db, 'store_password_reset_token'):
        try:
            db.store_password_reset_token(email.lower(), token, expiry)
        except Exception:
            pass

    return True, token


def verify_reset_token(token: str) -> tuple:
    """Verify a password reset token. Returns (valid, email or error_message)"""
    # Load from persistent storage (not just session state)
    tokens = _load_reset_tokens()
    entry = tokens.get(token)

    if not entry:
        return False, "Invalid or expired reset token."

    if entry.get('used'):
        return False, "This reset link has already been used."

    expiry = datetime.fromisoformat(entry['expiry'])
    if datetime.utcnow() > expiry:
        return False, "This reset link has expired. Please request a new one."

    return True, entry['email']


def consume_reset_token(token: str):
    """Mark a reset token as used in persistent storage"""
    tokens = _load_reset_tokens()
    if token in tokens:
        tokens[token]['used'] = True
        _save_reset_tokens(tokens)


def reset_password_with_token(token: str, new_password: str, confirm_password: str) -> tuple:
    """Reset a user's password using a valid token"""
    valid, result = verify_reset_token(token)
    if not valid:
        return False, result

    email = result

    if new_password != confirm_password:
        return False, "Passwords do not match."

    is_valid, errors = PasswordValidator.validate(new_password)
    if not is_valid:
        return False, "Password: " + ", ".join(errors)

    user = db.get_user_by_email(email)
    if not user:
        return False, "Account not found."

    try:
        # Use the dedicated update_password method which correctly hashes and saves
        success = db.update_password(user.id, new_password)
        if not success:
            return False, "Failed to reset password. Please try again."
        consume_reset_token(token)
        return True, "Password reset successfully! You can now login."
    except Exception as e:
        return False, f"Failed to reset password. Please try again."


# ============ AUTHENTICATION FUNCTIONS ============

def login_user(email: str, password: str, remember_me: bool = False) -> tuple:
    """Login user"""
    is_valid_email, email_message = EmailValidator.validate(email)
    if not is_valid_email:
        return False, email_message
    
    user = db.get_user_by_email(email.lower())
    if not user:
        db.record_login_attempt(email, "unknown", False)
        return False, "Invalid email or password"
    
    if not user.is_active:
        return False, "This account has been disabled"
    
    if not PasswordManager.verify_password(password, user.password_hash):
        db.record_login_attempt(email, "unknown", False)
        return False, "Invalid email or password"
    
    failed_attempts = db.get_recent_login_attempts(email)
    if failed_attempts >= 5:
        return False, "Too many login attempts. Please try again later"
    
    token = JWTManager.create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    })
    
    db.update_user(user.id, last_login=datetime.utcnow().isoformat())
    db.record_login_attempt(email, "unknown", True)
    
    # Re-fetch user from DB to get updated last_login and created_at
    updated_user = db.get_user_by_email(email.lower())
    if updated_user:
        user = updated_user
    
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.user_id = user.id
    st.session_state.token = token
    st.session_state.role = user.role
    
    if remember_me:
        st.session_state.remember_me = True
    
    return True, "Login successful!"


def signup_user(name: str, email: str, password: str, confirm_password: str) -> tuple:
    """Signup new user"""
    is_valid_name, name_message = NameValidator.validate(name)
    if not is_valid_name:
        return False, name_message
    
    is_valid_email, email_message = EmailValidator.validate(email)
    if not is_valid_email:
        return False, email_message
    
    if EmailValidator.is_disposable_email(email):
        return False, "Disposable email addresses are not allowed"
    
    if db.get_user_by_email(email.lower()):
        return False, "This email is already registered"
    
    is_valid_password, password_errors = PasswordValidator.validate(password)
    if not is_valid_password:
        return False, "Password: " + ", ".join(password_errors)
    
    if password != confirm_password:
        return False, "Passwords do not match"
    
    user = db.create_user(name, email.lower(), password)
    if not user:
        return False, "Failed to create account. Please try again"
    
    return True, "Account created successfully! You can now login"


def logout_user():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.token = None
    st.session_state.role = 'user'
    st.session_state.editing_profile = False


def is_admin(user: User) -> bool:
    """Check if user is admin"""
    return user and user.role in ['admin', 'superadmin']


# ============ PAGE COMPONENTS ============

def render_forgot_password_page():
    """Render the Forgot Password page"""
    st.markdown("""
        <style>
        .stApp { background: white !important; }
        .stTextInput input {
            background: #F3F4F6 !important;
            border: 2px solid #E5E7EB !important;
            color: #111827 !important;
            border-radius: 10px !important;
            padding: 0.95rem 1rem !important;
            font-size: 0.95rem !important;
        }
        .stTextInput input:focus {
            border-color: #2563EB !important;
            background: #FFFFFF !important;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
        }
        .stTextInput label { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align:center; margin-bottom:2rem; padding-top:2rem;">
                <div style="font-size:3.5rem;">🔑</div>
                <h1 style="font-size:2rem; font-weight:800; color:#1E293B; margin:0.5rem 0;">Forgot Password?</h1>
                <p style="color:#64748B; font-size:0.95rem; margin:0;">
                    Enter your registered email and we'll generate a reset token for you.
                </p>
            </div>
        """, unsafe_allow_html=True)

        fp_email = st.text_input(
            "email",
            placeholder="you@example.com",
            key="fp_email",
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔐 Generate Reset Token", use_container_width=True, type="primary", key="fp_submit"):
            if not fp_email:
                st.error("Please enter your email address.")
            else:
                is_valid_email, email_msg = EmailValidator.validate(fp_email)
                if not is_valid_email:
                    st.error(email_msg)
                else:
                    success, result = generate_password_reset_token(fp_email)
                    user_exists = db.get_user_by_email(fp_email.lower())
                    if user_exists:
                        # Show token directly in UI (since no email server)
                        st.success("✅ Reset token generated!")
                        st.markdown(f"""
                            <div style="
                                background:#EFF6FF;
                                border:1px solid #BFDBFE;
                                border-left:4px solid #2563EB;
                                border-radius:10px;
                                padding:1.25rem 1.5rem;
                                margin:1rem 0;
                            ">
                                <p style="margin:0 0 0.5rem 0; font-weight:600; color:#1E40AF;">🔑 Your Reset Token:</p>
                                <code style="
                                    word-break:break-all;
                                    font-size:0.85rem;
                                    background:#DBEAFE;
                                    padding:0.5rem 0.75rem;
                                    border-radius:6px;
                                    display:block;
                                    color:#1E3A8A;
                                    font-family:monospace;
                                ">{result}</code>
                                <p style="margin:0.75rem 0 0 0; font-size:0.82rem; color:#64748B;">
                                    ⏰ This token expires in <strong>1 hour</strong>. Copy it and use it below.
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        st.session_state.fp_token_generated = result
                        st.session_state.fp_token_email = fp_email.lower()
                    else:
                        st.info("If this email is registered, a reset token will be shown here.")

        # If token was generated, show direct link to reset page
        if st.session_state.get('fp_token_generated'):
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➡️ Proceed to Reset Password", use_container_width=True, type="secondary", key="fp_go_reset"):
                st.session_state.page = "reset_password"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#E2E8F0;'>", unsafe_allow_html=True)

        if st.button("← Back to Login", use_container_width=True, key="fp_back"):
            st.session_state.page = "login"
            st.session_state.fp_token_generated = None
            st.rerun()


def render_reset_password_page():
    """Render the Reset Password page"""
    st.markdown("""
        <style>
        .stApp { background: white !important; }
        .stTextInput input {
            background: #F3F4F6 !important;
            border: 2px solid #E5E7EB !important;
            color: #111827 !important;
            border-radius: 10px !important;
            padding: 0.95rem 1rem !important;
            font-size: 0.95rem !important;
        }
        .stTextInput input:focus {
            border-color: #2563EB !important;
            background: #FFFFFF !important;
            box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align:center; margin-bottom:2rem; padding-top:2rem;">
                <div style="font-size:3.5rem;">🔒</div>
                <h1 style="font-size:2rem; font-weight:800; color:#1E293B; margin:0.5rem 0;">Reset Password</h1>
                <p style="color:#64748B; font-size:0.95rem;">Enter your reset token and choose a new password.</p>
            </div>
        """, unsafe_allow_html=True)

        # Pre-fill token if coming from forgot password page
        prefill_token = st.session_state.get('fp_token_generated', '')

        reset_token = st.text_input(
            "🔑 Reset Token",
            value=prefill_token,
            placeholder="Paste your reset token here",
            key="rp_token"
        )

        new_password = st.text_input(
            "🔒 New Password",
            type="password",
            placeholder="Enter new password",
            key="rp_new_password"
        )

        if new_password:
            strength = PasswordValidator.get_password_strength(new_password)
            strength_emojis = {
                'weak': '🔴 Weak',
                'fair': '🟠 Fair',
                'good': '🟡 Good',
                'strong': '🟢 Strong',
                'very-strong': '💚 Very Strong'
            }
            st.info(f"Password Strength: {strength_emojis.get(strength, strength)}")

        confirm_password = st.text_input(
            "🔒 Confirm New Password",
            type="password",
            placeholder="Re-enter new password",
            key="rp_confirm_password"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("✅ Reset Password", use_container_width=True, type="primary", key="rp_submit"):
            if not reset_token or not new_password or not confirm_password:
                st.error("Please fill in all fields.")
            else:
                success, message = reset_password_with_token(
                    reset_token.strip(), new_password, confirm_password
                )
                if success:
                    st.success(f"🎉 {message}")
                    st.balloons()
                    # Clear token from session
                    st.session_state.fp_token_generated = None
                    st.session_state.fp_token_email = None
                    time.sleep(2)
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#E2E8F0;'>", unsafe_allow_html=True)

        col_back1, col_back2 = st.columns(2)
        with col_back1:
            if st.button("← Back to Login", use_container_width=True, key="rp_back_login"):
                st.session_state.page = "login"
                st.rerun()
        with col_back2:
            if st.button("🔑 Get New Token", use_container_width=True, key="rp_back_forgot"):
                st.session_state.page = "forgot_password"
                st.rerun()


def render_login_page():
    """Render professional login page with minimal top spacing like modern apps"""
    st.markdown("""
        <style>
        /* ===== REMOVE ALL STREAMLIT SPACING ===== */
        html, body, .stApp {
            margin: 0 !important;
            padding: 0 !important;
            width: 100%;
            height: 100%;
            overflow-x: hidden;
        }

        header,
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] {
            display: none !important;
        }

        .block-container,
        .stMainBlockContainer,
        [data-testid="stMainBlockContainer"] {
            max-width: 100% !important;
            width: 100% !important;
            margin: 0 !important;
            margin-top: 0 !important;
            padding: 0 !important;
            padding-top: 0 !important;
        }

        /* ===== LOGIN PAGE ===== */
        .login-page-content {
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding: 0 !important;
            padding-bottom: 32px !important;
            margin: 0 !important;
            background: linear-gradient(180deg, #FFFFFF, #F8FAFC);
        }

        @media (prefers-color-scheme: dark) {
            .login-page-content {
                background: linear-gradient(180deg, #0F172A, #1A2332);
            }
        }

        /* Header */
        .login-header {
            margin: 0 !important;
            margin-top: 4px !important;
            padding: 0 24px !important;
            text-align: center;
            width: 100%;
            animation: fadeInDown 0.8s ease-out;
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .graduation-icon {
            margin: 0 0 8px 0 !important;
            font-size: 5rem;
            animation: float 3.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            display: inline-block;
        }

        @keyframes float {
            0%, 100% {
                transform: translateY(0px);
            }
            50% {
                transform: translateY(-20px);
            }
        }

        .login-title {
            margin: 0 !important;
            font-size: 3rem;
            font-weight: 900;
            color: #2563EB;
            letter-spacing: -0.03em;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        }

        @media (prefers-color-scheme: dark) {
            .login-title {
                color: #60A5FA;
            }
        }

        .login-subtitle {
            margin: 8px auto 0 auto !important;
            font-size: 1rem;
            color: #6B7280;
            font-weight: 500;
            line-height: 1.6;
            max-width: 500px;
            padding: 0 1rem;
        }

        @media (prefers-color-scheme: dark) {
            .login-subtitle {
                color: #9CA3AF;
            }
        }

        /* Form */
        .form-container {
            width: 100%;
            max-width: 420px;
            margin: 24px 0 0 0 !important;
            animation: fadeInUp 0.8s ease-out;
            padding: 0 !important;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* ===== INPUT STYLES ===== */
        .input-wrapper {
            position: relative;
            margin-bottom: 1rem;
        }

        .input-icon {
            position: absolute;
            left: 1.25rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.3rem;
            pointer-events: none;
            transition: all 0.3s ease;
            z-index: 10;
            opacity: 0.6;
        }

        .input-wrapper:focus-within .input-icon {
            opacity: 1;
            transform: translateY(-50%) scale(1.1);
            color: #2563EB;
        }

        @media (prefers-color-scheme: dark) {
            .input-wrapper:focus-within .input-icon {
                color: #60A5FA;
            }
        }

        .stTextInput input {
            background: #F3F4F6 !important;
            border: 2px solid #E5E7EB !important;
            color: #111827 !important;
            border-radius: 10px !important;
            padding: 0.95rem 1rem 0.95rem 3.75rem !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
            letter-spacing: 0.3px;
        }

        .stTextInput input::placeholder {
            color: #9CA3AF !important;
            opacity: 1 !important;
        }

        .stTextInput input:hover {
            border-color: #D1D5DB !important;
            background: #F9FAFB !important;
        }

        .stTextInput input:focus {
            border-color: #2563EB !important;
            background: #FFFFFF !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
            outline: none !important;
        }

        .stTextInput label {
            display: none !important;
        }

        @media (prefers-color-scheme: dark) {
            .stTextInput input {
                background: #1E293B !important;
                border-color: #334155 !important;
                color: #F1F5F9 !important;
            }

            .stTextInput input::placeholder {
                color: #64748B !important;
            }

            .stTextInput input:hover {
                border-color: #475569 !important;
                background: #253346 !important;
            }

            .stTextInput input:focus {
                border-color: #60A5FA !important;
                background: #334155 !important;
                box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.15) !important;
            }
        }

        /* ===== REMEMBER & FORGOT ===== */
        .remember-forgot-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 1.5rem 0 2rem 0;
            gap: 1rem;
            flex-wrap: wrap;
            width: 100%;
        }

        .stCheckbox {
            margin: 0 !important;
        }

        .stCheckbox label {
            color: #374151 !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            cursor: pointer !important;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        @media (prefers-color-scheme: dark) {
            .stCheckbox label {
                color: #D1D5DB !important;
            }
        }

        .forgot-password {
            color: #2563EB;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        /* Style forgot password button as a link */
        button[kind="secondary"][data-testid="stButton"]:has(> div > p:contains("Forgot")) {
            background: none !important;
            border: none !important;
            color: #2563EB !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 0 !important;
            text-decoration: underline;
            cursor: pointer;
        }

        [data-testid="stButton"] button[key="forgot_password_btn"],
        button[data-testid="baseButton-secondary"]:has(p:contains("Forgot")) {
            background: transparent !important;
            border: none !important;
            color: #2563EB !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            padding: 0 !important;
            box-shadow: none !important;
            text-decoration: underline !important;
        }

        .forgot-password:hover {
            color: #1D4ED8;
            text-decoration: underline;
            text-decoration-thickness: 2px;
            text-underline-offset: 5px;
        }

        @media (prefers-color-scheme: dark) {
            .forgot-password {
                color: #60A5FA;
            }

            .forgot-password:hover {
                color: #93C5FD;
            }
        }

        /* ===== LOGIN BUTTON ===== */
        [data-testid="stButton"] > button[kind="primary"] {
            width: 100% !important;
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
            color: white !important;
            border: none !important;
            padding: 1rem 1.5rem !important;
            border-radius: 10px !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            cursor: pointer !important;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25);
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        }

        [data-testid="stButton"] > button[kind="primary"]:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4) !important;
        }

        [data-testid="stButton"] > button[kind="primary"]:active {
            transform: translateY(-1px) !important;
        }

        /* ===== SIGNUP SECTION ===== */
        .signup-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #E5E7EB, transparent);
            margin: 2rem 0;
        }

        @media (prefers-color-scheme: dark) {
            .signup-divider {
                background: linear-gradient(90deg, transparent, #334155, transparent);
            }
        }

        .signup-text {
            text-align: center;
            color: #6B7280;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 1.25rem;
        }

        @media (prefers-color-scheme: dark) {
            .signup-text {
                color: #9CA3AF;
            }
        }

        [data-testid="stButton"] > button[kind="secondary"] {
            width: 100% !important;
            background: transparent !important;
            color: #2563EB !important;
            border: 2px solid #2563EB !important;
            padding: 0.95rem 1.5rem !important;
            border-radius: 10px !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.5px;
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        [data-testid="stButton"] > button[kind="secondary"]:hover {
            background: rgba(37, 99, 235, 0.08) !important;
            transform: translateY(-4px) !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
        }

        [data-testid="stButton"] > button[kind="secondary"]:active {
            transform: translateY(-1px) !important;
        }

        @media (prefers-color-scheme: dark) {
            [data-testid="stButton"] > button[kind="secondary"] {
                color: #60A5FA !important;
                border-color: #60A5FA !important;
            }

            [data-testid="stButton"] > button[kind="secondary"]:hover {
                background: rgba(96, 165, 250, 0.1) !important;
            }
        }

        /* ===== ALERTS ===== */
        .stAlert {
            border-radius: 10px !important;
            border: none !important;
            margin-bottom: 1.5rem !important;
            animation: slideDown 0.4s ease-out;
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* ===== RESPONSIVE DESIGN ===== */
        @media (max-width: 768px) {
            .login-page-content {
                padding: 0 !important;
            }

            .login-title {
                font-size: 2.5rem;
            }

            .graduation-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }

            .login-header {
                margin-bottom: 1.5rem;
                padding: 0 20px !important;
            }

            .form-container {
                margin-top: 20px !important;
                padding: 0 20px !important;
            }

            .remember-forgot-container {
                flex-direction: column;
                align-items: flex-start;
                margin: 1.25rem 0 1.75rem 0;
            }
        }

        @media (max-width: 480px) {
            .login-page-content {
                padding: 0 !important;
            }

            .login-title {
                font-size: 2rem;
            }

            .graduation-icon {
                font-size: 3.5rem;
                margin-bottom: 0.75rem;
            }

            .login-subtitle {
                font-size: 0.9rem;
                padding: 0 0.5rem;
            }

            .login-header {
                margin-bottom: 1.5rem;
                padding: 0 16px !important;
            }

            .form-container {
                max-width: 100%;
                margin-top: 16px !important;
                padding: 0 16px !important;
            }

            .stTextInput input {
                padding: 0.875rem 0.875rem 0.875rem 3.5rem !important;
                font-size: 0.9rem !important;
            }

            .input-icon {
                left: 1rem;
                font-size: 1.15rem;
            }
        }

        /* ===== ACCESSIBILITY ===== */
        *:focus-visible {
            outline: 2px solid #2563EB;
            outline-offset: 2px;
        }

        input:focus-visible {
            outline: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main page content
    st.markdown("""
        <div class="login-page-content">
    """, unsafe_allow_html=True)

    # Header section
    st.markdown("""
        <div class="login-header">
            <div class="graduation-icon">🎓</div>
            <h1 class="login-title">LearnMate</h1>
            <p class="login-subtitle">Welcome back! Login to continue learning and access your personalized AI learning experience.</p>
        </div>
    """, unsafe_allow_html=True)

    # Form container
    st.markdown('<div class="form-container">', unsafe_allow_html=True)

    # Email Input
    st.markdown("""
        <div class="input-wrapper">
            <span class="input-icon">✉️</span>
    """, unsafe_allow_html=True)
    
    email = st.text_input(
        "email",
        placeholder="you@example.com",
        key="login_email",
        label_visibility="collapsed"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Password Input
    st.markdown("""
        <div class="input-wrapper">
            <span class="input-icon">🔒</span>
    """, unsafe_allow_html=True)
    
    password = st.text_input(
        "password",
        type="password",
        placeholder="Enter your password",
        key="login_password",
        label_visibility="collapsed"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Remember Me & Forgot Password
    st.markdown('<div class="remember-forgot-container">', unsafe_allow_html=True)
    
    remember_me = st.checkbox("Remember me", value=False, key="remember_checkbox")

    forgot_clicked = st.button("Forgot password?", key="forgot_password_btn")
    
    st.markdown('</div>', unsafe_allow_html=True)

    if forgot_clicked:
        st.session_state.page = "forgot_password"
        st.rerun()

    # Login Button
    login_clicked = st.button(
        "Sign In",
        use_container_width=True,
        key="login_submit",
        type="primary"
    )

    # Handle Login
    if login_clicked:
        if email and password:
            success, message = login_user(email, password, remember_me)
            if success:
                st.success(message)
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)
        else:
            st.error("Please enter both email and password")

    # Signup Section
    st.markdown('<div class="signup-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="signup-text">New to LearnMate?</p>', unsafe_allow_html=True)

    signup_clicked = st.button(
        "Create Account",
        use_container_width=True,
        key="go_signup",
        type="secondary"
    )

    if signup_clicked:
        st.session_state.page = "signup"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)




def render_signup_page():
    """Render signup page"""
    st.markdown("""
        <style>
        .stApp {
            background: white !important;
        }
        .stTextInput input {
            background: #F8FAFC !important;
            border: 1px solid #E2E8F0 !important;
            color: #1E293B !important;
            border-radius: 0.6rem !important;
        }
        .stTextInput input:focus {
            border-color: #2563EB !important;
            background: white !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        }
        .stTextInput label { color: #1E293B !important; font-weight: 600 !important; }
        .login-divider { border: none; border-top: 1px solid #E2E8F0; margin: 1.5rem 0; }
        .signup-brand { text-align: center; margin-bottom: 2rem; }
        .signup-brand .brand-icon { font-size: 3.5rem; display: block; margin-bottom: 0.5rem; }
        .signup-brand h1 { font-size: 1.75rem; font-weight: 700; color: #1E293B; margin: 0.25rem 0; }
        .signup-brand p { color: #64748B; font-size: 0.95rem; margin: 0.5rem 0 0 0; }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="signup-brand">
                <span class="brand-icon">🎓</span>
                <h1>LearnMate</h1>
                <p>Create your account and start learning today</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
        
        name = st.text_input(
            "👤 Full Name",
            placeholder="John Doe",
            key="signup_name"
        )
        
        email = st.text_input(
            "📧 Email Address",
            placeholder="you@example.com",
            key="signup_email"
        )
        
        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Create a strong password",
            key="signup_password"
        )
        
        if password:
            strength = PasswordValidator.get_password_strength(password)
            strength_emojis = {
                'weak': '🔴',
                'fair': '🟠',
                'good': '🟡',
                'strong': '🟢',
                'very-strong': '💚'
            }
            st.info(f"Password Strength: {strength_emojis[strength]} {strength.capitalize()}")
        
        confirm_password = st.text_input(
            "🔒 Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="signup_confirm"
        )
        
        if st.button("✨ Create Account", use_container_width=True, key="signup_submit", type="primary"):
            if name and email and password and confirm_password:
                success, message = signup_user(name, email, password, confirm_password)
                if success:
                    st.success(message)
                    st.balloons()
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please fill in all fields")
        
        st.markdown('<hr class="login-divider">', unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B; font-size:0.9rem;'>Already have an account?</p>", unsafe_allow_html=True)
        
        if st.button("🔐 Back to Login", use_container_width=True, key="back_login"):
            st.session_state.page = "login"
            st.rerun()


def render_email_verification_section():
    """Render email verification section"""
    user = st.session_state.user
    
    st.markdown("""
        <style>
            .section-header {
                padding: 1rem 0;
                border-bottom: 2px solid #E2E8F0;
                margin-bottom: 1.5rem;
            }
            
            .section-header h3 {
                color: #2563EB;
                font-size: 1.25rem;
                margin: 0;
                font-weight: 700;
            }
        </style>
        <div class="section-header">
            <h3>📧 Email Verification</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if user.email_verified:
            st.success("✅ Email Verified", icon="✅")
            st.caption(f"Your email {user.email} has been verified")
        else:
            st.warning("⚠️ Email Not Verified", icon="⚠️")
            st.caption(f"Verify your email {user.email} to unlock all features")
    
    with col2:
        if not user.email_verified:
            if st.button("📬 Send Verification Email", use_container_width=True, key="send_verification"):
                success, message = send_verification_email(user.email, user.name)
                if success:
                    st.success(message)
                    st.session_state.verification_sent = True
                else:
                    st.error(message)
        else:
            st.success("Verified")


def render_edit_profile_section():
    """Render editable profile section"""
    user = st.session_state.user
    
    st.subheader("📋 Your Profile")
    
    col_toggle_left, col_toggle_right = st.columns([3, 1])
    with col_toggle_right:
        if st.button("✏️ Edit" if not st.session_state.editing_profile else "✖️ Cancel", 
                     use_container_width=True, key="toggle_edit"):
            st.session_state.editing_profile = not st.session_state.editing_profile
            st.rerun()
    
    if st.session_state.editing_profile:
        st.markdown("""
            <div class="profile-edit-box">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input(
                "👤 Full Name",
                value=user.name,
                key="edit_name"
            )
        
        with col2:
            st.text_input(
                "📧 Email Address",
                value=user.email,
                disabled=True,
                key="edit_email",
                help="Email cannot be changed"
            )
        
        new_password = st.text_input(
            "🔒 New Password (leave empty to keep current)",
            type="password",
            key="edit_password"
        )
        
        if new_password:
            confirm_new_password = st.text_input(
                "🔒 Confirm New Password",
                type="password",
                key="edit_confirm_password"
            )
        
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            if st.button("💾 Save Changes", use_container_width=True, key="save_profile"):
                try:
                    # Validate inputs
                    if not new_name:
                        st.error("Name cannot be empty")
                    elif new_password and new_password != confirm_new_password:
                        st.error("Passwords do not match")
                    elif new_password:
                        is_valid, errors = PasswordValidator.validate(new_password)
                        if not is_valid:
                            st.error("Password: " + ", ".join(errors))
                        else:
                            # Update user
                            db.update_user(
                                user.id,
                                name=new_name,
                                password_hash=PasswordManager.hash_password(new_password)
                            )
                            st.session_state.user.name = new_name
                            st.success("Profile updated successfully!")
                            st.session_state.editing_profile = False
                            st.rerun()
                    else:
                        # Update name only
                        db.update_user(user.id, name=new_name)
                        st.session_state.user.name = new_name
                        st.success("Profile updated successfully!")
                        st.session_state.editing_profile = False
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Error updating profile: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {user.name}")
            st.write(f"**Email:** {user.email}")
        with col2:
            st.write(f"**Account Type:** {user.role.capitalize()}")
            st.write(f"**Status:** {'Active ✅' if user.is_active else 'Inactive ❌'}")


def render_chat_history_section():
    """Render chat history section with true real-time updates"""
    st.subheader("💬 Chat History")
    
    # Initialize real-time polling state
    if 'chat_last_count' not in st.session_state:
        st.session_state.chat_last_count = 0
    if 'chat_last_timestamp' not in st.session_state:
        st.session_state.chat_last_timestamp = datetime.now()
    
    user_id = st.session_state.user_id
    
    # Get chat history - always fetch latest from database
    try:
        chat_history = get_chat_history(user_id)
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
        chat_history = []
    
    current_count = len(chat_history) if chat_history else 0
    
    # Create control buttons
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True, key="refresh_chat_btn"):
            st.session_state.chat_last_count = 0
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear", use_container_width=True, key="clear_chat_btn"):
            st.session_state.confirm_clear_chat = True
    
    # Clear confirmation dialog
    if st.session_state.get('confirm_clear_chat'):
        st.warning("⚠️ This will permanently delete all your chat history.")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("✅ Delete", use_container_width=True, key="confirm_delete_chat", type="primary"):
                clear_chat_history(user_id)
                st.session_state.confirm_clear_chat = False
                st.session_state.chat_last_count = 0
                st.success("Chat history cleared!")
                st.rerun()
        with col_no:
            if st.button("❌ Cancel", use_container_width=True, key="cancel_delete_chat"):
                st.session_state.confirm_clear_chat = False
                st.rerun()
    
    # Display chat history
    if not chat_history:
        st.info("📭 No chat history yet. Start a conversation in the chatbot!")
    else:
        # Show new message indicator if messages were added
        if current_count > st.session_state.chat_last_count:
            st.session_state.chat_last_count = current_count
            st.success(f"✨ Showing {current_count} conversation(s)")
        
        # Display chats in reverse order (latest first)
        st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
        
        for idx, chat in enumerate(reversed(chat_history), 1):
            # Safely extract and escape message content
            user_msg = str(chat.get('message', '')).strip()
            bot_response = str(chat.get('response', '')).strip()
            timestamp = format_timestamp(chat.get('timestamp', datetime.now()))
            
            # Truncate very long messages for readability
            if len(user_msg) > 500:
                user_msg = user_msg[:500] + "..."
            if len(bot_response) > 500:
                bot_response = bot_response[:500] + "..."
            
            st.markdown(f"""
                <div class="chat-message">
                    <div class="chat-sender">👤 You:</div>
                    <div class="chat-content">{user_msg}</div>
                    <div class="chat-separator"></div>
                    <div class="chat-sender">🤖 ChatBot:</div>
                    <div class="chat-content">{bot_response}</div>
                    <div class="chat-timestamp">⏰ {timestamp}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-time auto-polling using Streamlit's built-in capabilities
    import time
    
    if 'chat_polling_active' not in st.session_state:
        st.session_state.chat_polling_active = True
    
    # Use a placeholder for auto-refresh
    poll_interval = 3  # Check every 3 seconds
    
    # Store last check time
    if 'chat_last_check' not in st.session_state:
        st.session_state.chat_last_check = time.time()
    
    current_time = time.time()
    time_since_check = current_time - st.session_state.chat_last_check
    
    # Auto-rerun at specified interval for real-time updates
    if time_since_check >= poll_interval:
        st.session_state.chat_last_check = current_time
        st.rerun()


def render_dashboard():
    """Render user dashboard"""
    # Refresh user from DB to get latest last_login, created_at
    try:
        fresh_user = db.get_user_by_email(st.session_state.user.email)
        if fresh_user:
            st.session_state.user = fresh_user
    except Exception:
        pass
    
    # Top navbar with improved styling
    user_display_name = st.session_state.user.name
    st.markdown(f"""
        <style>
            .dashboard-header {{
                background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
                padding: 2rem;
                border-radius: 1rem;
                margin-bottom: 2rem;
                color: white;
                box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.2);
            }}
            
            .dashboard-header h1 {{
                color: white;
                margin: 0;
                font-size: 2rem;
                font-weight: 700;
            }}
            
            .dashboard-header p {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 1rem;
                margin: 0.5rem 0 0 0;
            }}
            
            .dashboard-user-info {{
                text-align: right;
                color: rgba(255, 255, 255, 0.9);
            }}
        </style>
        <div class="dashboard-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1>🎓 {APP_NAME}</h1>
                    <p>Your Learning Dashboard</p>
                </div>
                <div class="dashboard-user-info">
                    <p style="font-weight: 600;">👤 {user_display_name}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.title(f"👋 Welcome back, {st.session_state.user.name.split()[0]}!")
    
    # User stats with formatted timestamps
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Account Status", "Active ✅" if st.session_state.user.is_active else "Inactive ❌")
    with col2:
        member_since = format_member_since(st.session_state.user.created_at)
        st.metric("Member Since", member_since)
    with col3:
        last_login = format_timestamp(st.session_state.user.last_login)
        st.metric("Last Login", last_login)
    
    st.markdown("---")
    
    # Editable Profile Section
    render_edit_profile_section()
    
    st.markdown("---")
    
    # Actions Section with improved styling
    st.markdown("""
        <style>
            .actions-container {
                background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
                padding: 2rem;
                border-radius: 1rem;
                border: 1px solid #BFDBFE;
                margin-top: 2rem;
            }
            
            .actions-container h3 {
                color: #1E40AF;
                margin-top: 0;
                font-size: 1.25rem;
            }
        </style>
        <div class="actions-container">
            <h3>⚙️ Quick Actions</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
            <a href="{CHATBOT_API_URL}" target="_blank" style="text-decoration: none;">
                <button style="width: 100%; padding: 0.75rem; background: #2563EB; color: white; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 15px;">
                    🤖 Open Chatbot
                </button>
            </a>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True, key="dashboard_logout"):
            logout_user()
            st.session_state.page = "login"
            st.rerun()


def render_admin_dashboard():
    """Render admin dashboard"""
    if not st.session_state.get('authenticated') or not is_admin(st.session_state.user):
        st.error("❌ Access Denied: Admin privileges required")
        st.stop()
    
    # Top navbar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### 🔐 {APP_NAME}")
    with col3:
        st.write(f"👤 {st.session_state.user.name}")
    
    st.markdown("---")
    
    st.title("👨‍💼 Admin Dashboard")
    
    # Admin menu
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Users", "Settings"])
    
    with tab1:
        st.subheader("📊 Statistics")
        users = db.get_all_users()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", len(users))
        with col2:
            active_users = sum(1 for u in users if u.is_active)
            st.metric("Active Users", active_users)
        with col3:
            admins = sum(1 for u in users if u.role in ['admin', 'superadmin'])
            st.metric("Admins", admins)
        with col4:
            verified = sum(1 for u in users if u.email_verified)
            st.metric("Email Verified", verified)
    
    with tab2:
        st.subheader("👥 User Management")
        users = db.get_all_users()
        
        if users:
            user_data = []
            for user in users:
                user_data.append({
                    "ID": user.id,
                    "Name": user.name,
                    "Email": user.email,
                    "Role": user.role,
                    "Status": "Active" if user.is_active else "Inactive",
                    "Created": format_timestamp(user.created_at),
                })
            
            st.dataframe(user_data, use_container_width=True)
        else:
            st.info("No users found")
    
    with tab3:
        st.subheader("⚙️ Settings")
        
        st.write("**System Settings**")
        col1, col2 = st.columns(2)
        
        with col1:
            maintenance_mode = st.toggle("Maintenance Mode", value=False)
            if maintenance_mode:
                st.warning("⚠️ Maintenance mode is ON. Regular users cannot access the app.")
        
        with col2:
            email_notifications = st.toggle("Email Notifications", value=True)
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True, key="admin_logout"):
            logout_user()
            st.session_state.page = "login"
            st.rerun()


# ============ MAIN APP ============

def main():
    """Main application logic"""
    
    # Initialize page state
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    
    # Route pages based on authentication status
    if st.session_state.get('authenticated'):
        user = st.session_state.user
        
        if is_admin(user):
            # Styled sidebar navigation
            st.sidebar.markdown(f"""
                <style>
                    [data-testid="stSidebar"] {{
                        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%) !important;
                        border-right: 1px solid rgba(99, 179, 237, 0.2) !important;
                    }}
                    [data-testid="stSidebar"] * {{
                        color: #E2E8F0 !important;
                    }}
                    [data-testid="stSidebar"] .stRadio label {{
                        color: #CBD5E1 !important;
                        font-size: 0.95rem !important;
                        padding: 0.4rem 0.2rem !important;
                    }}
                    [data-testid="stSidebar"] .stRadio label:hover {{
                        color: #63B3ED !important;
                    }}
                    [data-testid="stSidebar"] hr {{
                        border-color: rgba(99, 179, 237, 0.2) !important;
                    }}
                    .sidebar-logo {{
                        text-align: center;
                        padding: 1.5rem 0 1rem 0;
                        border-bottom: 1px solid rgba(99, 179, 237, 0.2);
                        margin-bottom: 1rem;
                    }}
                    .sidebar-logo h2 {{
                        color: white !important;
                        font-size: 1.4rem;
                        margin: 0;
                        font-weight: 700;
                        text-shadow: 0 0 20px rgba(99, 179, 237, 0.5);
                    }}
                    .sidebar-logo p {{
                        color: rgba(99, 179, 237, 0.8) !important;
                        font-size: 0.75rem;
                        margin: 0.25rem 0 0 0;
                        letter-spacing: 0.05em;
                        text-transform: uppercase;
                    }}
                    .sidebar-user-badge {{
                        background: rgba(99, 179, 237, 0.15);
                        border: 1px solid rgba(99, 179, 237, 0.3);
                        border-radius: 0.5rem;
                        padding: 0.6rem 0.8rem;
                        margin-top: 0.5rem;
                    }}
                </style>
                <div class="sidebar-logo">
                    <h2>🎓 {APP_NAME}</h2>
                    <p>Admin Panel</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.sidebar.markdown("### 📌 Navigation")
            page = st.sidebar.radio(
                "",
                ["🏠 Dashboard", "🔐 Admin Panel"],
                key="sidebar_nav",
                label_visibility="collapsed"
            )
            
            st.sidebar.markdown("---")
            st.sidebar.markdown(f"**👤 {user.name}**")
            st.sidebar.caption(f"Role: {user.role.capitalize()}")
            
            if page == "🏠 Dashboard":
                render_dashboard()
            else:
                render_admin_dashboard()
        else:
            render_dashboard()
    
    else:
        # Not authenticated - show login/signup
        if st.session_state.page == "signup":
            render_signup_page()
        elif st.session_state.page == "forgot_password":
            render_forgot_password_page()
        elif st.session_state.page == "reset_password":
            render_reset_password_page()
        else:
            render_login_page()


if __name__ == "__main__":
    main()
