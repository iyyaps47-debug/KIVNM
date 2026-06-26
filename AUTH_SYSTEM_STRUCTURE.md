# Authentication System - Project Structure

```
chatbot-auth-system/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── config.py                       # Configuration settings
├── database.py                     # Database connection and setup
│
├── auth/
│   ├── __init__.py
│   ├── models.py                   # User and Admin models
│   ├── security.py                 # Password hashing, JWT, encryption
│   ├── validators.py               # Email and password validation
│   ├── email_service.py            # Email sending for password reset
│   └── rate_limiter.py             # Rate limiting for login attempts
│
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py              # Login, Signup, Logout endpoints
│   ├── user_routes.py              # User profile management
│   └── admin_routes.py             # Admin dashboard endpoints
│
├── pages/
│   ├── 01_Login.py                 # Login page
│   ├── 02_Signup.py                # Signup page
│   ├── 03_Dashboard.py             # User dashboard
│   ├── 04_Chatbot.py               # Main chatbot (protected)
│   └── 05_Admin.py                 # Admin dashboard
│
├── components/
│   ├── __init__.py
│   ├── navbar.py                   # Navigation bar
│   ├── footer.py                   # Footer
│   └── auth_middleware.py          # Authentication checks
│
├── static/
│   ├── css/
│   │   ├── login.css               # Login page styles
│   │   ├── signup.css              # Signup page styles
│   │   └── global.css              # Global styles
│   └── js/
│       ├── auth.js                 # Authentication logic
│       └── utils.js                # Utility functions
│
├── templates/
│   ├── login.html                  # Login HTML
│   ├── signup.html                 # Signup HTML
│   └── emails/
│       └── reset_password.html      # Password reset email template
│
└── database/
    ├── schema.sql                  # Database schema
    └── init_db.py                  # Database initialization
```
