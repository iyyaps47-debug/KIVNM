# 🔌 Integration Examples & API Usage

## Frontend Integration

### 1. Login Integration with Existing Chatbot

```html
<!-- In your chatbot's HTML template -->
<!DOCTYPE html>
<html>
<head>
    <title>SkillzLearn Chatbot</title>
</head>
<body>
    <!-- Check if user is authenticated -->
    <script>
        // Get token from session/localStorage
        const token = sessionStorage.getItem('auth_token');
        
        if (!token) {
            // Redirect to login
            window.location.href = '/login';
        } else {
            // Verify token validity
            fetch('/api/verify-token', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(response => {
                if (!response.ok) {
                    sessionStorage.removeItem('auth_token');
                    window.location.href = '/login';
                }
            });
        }
    </script>
    
    <div class="navbar">
        <span id="user-name"></span>
        <button onclick="logout()">Logout</button>
    </div>
    
    <!-- Your chatbot content -->
    <div id="chatbot-container"></div>
    
    <script>
        // Load user profile
        function loadUserProfile() {
            const token = sessionStorage.getItem('auth_token');
            
            fetch('/api/user/profile', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('user-name').textContent = `Welcome, ${data.name}!`;
            });
        }
        
        // Logout function
        function logout() {
            const token = sessionStorage.getItem('auth_token');
            
            fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            .then(() => {
                sessionStorage.removeItem('auth_token');
                window.location.href = '/login';
            });
        }
        
        // Initialize
        loadUserProfile();
    </script>
</body>
</html>
```

### 2. Store Token in Browser (Secure Method)

```javascript
// Save token with expiration
function saveAuthToken(token, expiresIn = 30) {
    const expiryDate = new Date();
    expiryDate.setMinutes(expiryDate.getMinutes() + expiresIn);
    
    // Use sessionStorage (cleared when browser closes)
    sessionStorage.setItem('auth_token', token);
    sessionStorage.setItem('auth_expires', expiryDate.toISOString());
}

// Check if token is expired
function isTokenExpired() {
    const expiryDate = sessionStorage.getItem('auth_expires');
    if (!expiryDate) return true;
    
    return new Date() > new Date(expiryDate);
}

// Get valid token or refresh
async function getValidToken() {
    if (!isTokenExpired()) {
        return sessionStorage.getItem('auth_token');
    }
    
    // Token expired, refresh it
    return await refreshToken();
}

// Refresh token
async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const response = await fetch('/api/refresh-token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: refreshToken })
    });
    
    if (response.ok) {
        const data = await response.json();
        saveAuthToken(data.token, data.expiresIn);
        localStorage.setItem('refresh_token', data.refresh_token);
        return data.token;
    }
    
    // Refresh failed, redirect to login
    window.location.href = '/login';
}
```

### 3. Protected API Calls

```javascript
// Make authenticated API call
async function apiCall(url, options = {}) {
    const token = await getValidToken();
    
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        // Unauthorized, redirect to login
        window.location.href = '/login';
        return null;
    }
    
    return response.json();
}

// Example: Get user data
async function getUserData() {
    return await apiCall('/api/user/profile');
}

// Example: Send message to chatbot
async function sendChatMessage(message) {
    return await apiCall('/api/chat/send', {
        method: 'POST',
        body: JSON.stringify({ message })
    });
}
```

---

## Backend Integration

### 1. Protect Routes with Middleware

```python
from functools import wraps
from auth_security import JWTManager
from database import db
from flask import request, jsonify

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # Verify token
        payload = JWTManager.decode_token(token)
        if not payload:
            return jsonify({'message': 'Token is invalid or expired'}), 401
        
        # Get user from database
        user = db.get_user_by_id(payload['user_id'])
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Pass user to route
        request.user = user
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.user.role not in ['admin', 'superadmin']:
            return jsonify({'message': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated
```

### 2. Protected Routes Example

```python
from flask import Flask, request, jsonify, render_template
from decorators import token_required, admin_required
from database import db
from auth_security import PasswordManager, JWTManager
from validators import EmailValidator, PasswordValidator

app = Flask(__name__)

# ============ USER ROUTES ============

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_user_profile():
    return jsonify({
        'id': request.user.id,
        'name': request.user.name,
        'email': request.user.email,
        'role': request.user.role,
        'created_at': request.user.created_at,
        'last_login': request.user.last_login
    })


@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_user_profile():
    data = request.json
    
    # Validate input
    if 'name' in data:
        is_valid, message = NameValidator.validate(data['name'])
        if not is_valid:
            return jsonify({'message': message}), 400
    
    # Update user
    user = db.update_user(request.user.id, **data)
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    })


@app.route('/api/user/change-password', methods=['POST'])
@token_required
def change_password():
    data = request.json
    
    # Verify current password
    if not PasswordManager.verify_password(
        data['current_password'],
        request.user.password_hash
    ):
        return jsonify({'message': 'Current password is incorrect'}), 400
    
    # Validate new password
    is_valid, errors = PasswordValidator.validate(data['new_password'])
    if not is_valid:
        return jsonify({'message': ', '.join(errors)}), 400
    
    # Update password
    if db.update_password(request.user.id, data['new_password']):
        return jsonify({'message': 'Password changed successfully'})
    
    return jsonify({'message': 'Failed to change password'}), 500


# ============ ADMIN ROUTES ============

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    users = db.get_all_users()
    
    return jsonify({
        'users': [u.to_dict() for u in users],
        'total': len(users)
    })


@app.route('/api/admin/user/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = db.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(user.to_dict())


@app.route('/api/admin/user/<int:user_id>', methods=['PUT'])
@admin_required
def update_user_admin(user_id):
    data = request.json
    
    user = db.update_user(user_id, **data)
    
    # Log admin action
    db.log_admin_action(
        admin_id=request.user.id,
        action='UPDATE_USER',
        target_user_id=user_id,
        ip_address=request.remote_addr,
        details=f'Updated user: {data}'
    )
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    })


@app.route('/api/admin/user/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user_admin(user_id):
    # Prevent deleting own account
    if user_id == request.user.id:
        return jsonify({'message': 'Cannot delete your own account'}), 400
    
    if db.delete_user(user_id):
        # Log admin action
        db.log_admin_action(
            admin_id=request.user.id,
            action='DELETE_USER',
            target_user_id=user_id,
            ip_address=request.remote_addr,
            details='Deleted user account'
        )
        
        return jsonify({'message': 'User deleted successfully'})
    
    return jsonify({'message': 'Failed to delete user'}), 500


@app.route('/api/admin/logs', methods=['GET'])
@admin_required
def get_admin_logs():
    # Get logs from database
    # This would require adding a method to get logs
    return jsonify({'logs': []})


# ============ CHATBOT INTEGRATION ============

@app.route('/api/chat/send', methods=['POST'])
@token_required
def send_message():
    data = request.json
    message = data.get('message')
    
    if not message:
        return jsonify({'message': 'Message is required'}), 400
    
    # Call your existing chatbot API
    # Store message in database
    
    return jsonify({
        'response': 'Chatbot response here',
        'user_id': request.user.id
    })


if __name__ == '__main__':
    app.run(debug=True)
```

---

## Streamlit Integration

### 1. Integrate with Existing Streamlit Chatbot

```python
# In your existing chatbot app
import streamlit as st
import sys
from pathlib import Path

# Import auth modules
sys.path.append(str(Path(__file__).parent))
from database import db
from auth_security import JWTManager

# Check authentication
def check_auth():
    if 'token' not in st.session_state:
        st.error("Please login first")
        st.stop()
    
    # Verify token
    payload = JWTManager.decode_token(st.session_state.token)
    if not payload:
        st.error("Session expired. Please login again")
        st.session_state.clear()
        st.rerun()
    
    return payload

# In your chatbot page
st.set_page_config(page_title="Chatbot", layout="wide")

# Check if user is authenticated
if 'token' not in st.session_state or not st.session_state.authenticated:
    st.error("Access Denied: Please login first")
    st.stop()

payload = check_auth()
user = db.get_user_by_id(payload['user_id'])

st.header(f"Welcome, {user.name}!")

# Your chatbot code here
chat_input = st.text_input("Ask me anything...")

if chat_input:
    # Store message in database
    # Get response from your chatbot
    # Display response
    pass
```

### 2. Multi-page Streamlit App Structure

```python
# pages/01_Login.py
import streamlit as st
from database import db
from auth_security import PasswordManager, JWTManager

st.set_page_config(page_title="Login", layout="centered")

if st.session_state.get('authenticated'):
    st.switch_page("pages/02_Dashboard.py")

st.title("Login")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = db.get_user_by_email(email)
    
    if user and PasswordManager.verify_password(password, user.password_hash):
        token = JWTManager.create_access_token({
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        })
        
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.token = token
        st.success("Login successful!")
        st.switch_page("pages/02_Dashboard.py")
    else:
        st.error("Invalid email or password")
```

```python
# pages/02_Dashboard.py
import streamlit as st
from database import db

st.set_page_config(page_title="Dashboard", layout="wide")

if not st.session_state.get('authenticated'):
    st.error("Please login first")
    st.stop()

user = st.session_state.get('user')

st.title(f"Dashboard - {user.name}")

# Your dashboard content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Email", user.email)

with col2:
    st.metric("Role", user.role)

with col3:
    st.metric("Member Since", user.created_at.split('T')[0])

# Navigation
page = st.radio("Select Page", ["Home", "Chatbot", "Profile", "Logout"])

if page == "Logout":
    st.session_state.clear()
    st.success("Logged out successfully!")
    st.switch_page("pages/01_Login.py")
```

---

## Database Integration

### 1. Custom Queries

```python
from database import db
import sqlite3

# Get custom statistics
def get_user_statistics():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_users,
            SUM(CASE WHEN email_verified = 1 THEN 1 ELSE 0 END) as verified_users,
            SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_count,
            SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_users
        FROM users
    ''')
    
    result = cursor.fetchone()
    conn.close()
    
    return {
        'total_users': result[0],
        'verified_users': result[1],
        'admin_count': result[2],
        'active_users': result[3]
    }


# Get user activity
def get_user_activity(user_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM chat_history 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''', (user_id,))
    
    messages = cursor.fetchall()
    conn.close()
    
    return [dict(msg) for msg in messages]
```

### 2. Bulk Operations

```python
def bulk_update_user_role(user_ids, new_role):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    placeholders = ','.join('?' * len(user_ids))
    
    cursor.execute(f'''
        UPDATE users SET role = ? 
        WHERE id IN ({placeholders})
    ''', [new_role] + user_ids)
    
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    return affected


def bulk_delete_inactive_users(days=90):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM users 
        WHERE is_active = 0 
        AND datetime(updated_at) < datetime('now', '-' || ? || ' days')
    ''', (days,))
    
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    
    return deleted
```

---

## Error Handling & Validation

### Comprehensive Error Handler

```python
from functools import wraps
from flask import jsonify

class APIError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code


def handle_api_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            return jsonify({'error': e.message}), e.status_code
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500
    
    return decorated_function


# Use in routes
@app.route('/api/endpoint')
@handle_api_errors
def my_endpoint():
    if some_condition:
        raise APIError('Something went wrong', 400)
    
    return jsonify({'success': True})
```

---

## Testing

### Unit Tests

```python
import unittest
from database import db
from auth_security import PasswordManager, JWTManager
from validators import EmailValidator, PasswordValidator

class TestAuth(unittest.TestCase):
    
    def setUp(self):
        # Setup test database
        self.db = Database(':memory:')
    
    def test_password_hashing(self):
        password = "TestPassword123!"
        hashed = PasswordManager.hash_password(password)
        
        self.assertTrue(
            PasswordManager.verify_password(password, hashed)
        )
    
    def test_email_validation(self):
        valid_email = "test@example.com"
        is_valid, msg = EmailValidator.validate(valid_email)
        
        self.assertTrue(is_valid)
    
    def test_password_validation(self):
        weak_password = "weak"
        is_valid, errors = PasswordValidator.validate(weak_password)
        
        self.assertFalse(is_valid)
        self.assertTrue(len(errors) > 0)
    
    def test_user_creation(self):
        user = self.db.create_user(
            "Test User",
            "test@example.com",
            "TestPassword123!"
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Test User")
    
    def test_jwt_token(self):
        token = JWTManager.create_access_token({"user_id": 1})
        payload = JWTManager.decode_token(token)
        
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], 1)


if __name__ == '__main__':
    unittest.main()
```

---

## Performance Tips

1. **Database Indexing**
   ```python
   CREATE INDEX idx_users_email ON users(email);
   CREATE INDEX idx_users_role ON users(role);
   CREATE INDEX idx_login_attempts_email ON login_attempts(email);
   ```

2. **Caching User Data**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def get_user_by_id(user_id):
       return db.get_user_by_id(user_id)
   ```

3. **Async Operations**
   ```python
   import asyncio
   
   async def send_email_async(email, content):
       await asyncio.to_thread(send_email, email, content)
   ```

---

This comprehensive integration guide covers all aspects of integrating the authentication system with your existing Streamlit chatbot application!
