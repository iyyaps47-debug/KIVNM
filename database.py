import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from auth_security import PasswordManager, JWTManager
from config import DATABASE_URL, DB_PATH
import os


class User:
    """User model for database"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        name: str = None,
        email: str = None,
        password_hash: str = None,
        is_active: bool = True,
        email_verified: bool = False,
        role: str = "user",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        last_login: Optional[str] = None,
        profile_picture: Optional[str] = None,
        bio: Optional[str] = None
    ):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.email_verified = email_verified
        self.role = role
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
        self.last_login = last_login
        self.profile_picture = profile_picture
        self.bio = bio
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login,
            "profile_picture": self.profile_picture,
            "bio": self.bio
        }


class Database:
    """Database connection and management"""
    
    def __init__(self, db_path: str = DB_PATH):
        """Initialize database"""
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database schema"""
        if not os.path.exists(self.db_path):
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    email_verified BOOLEAN DEFAULT 0,
                    role TEXT DEFAULT 'user',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_login TEXT,
                    profile_picture TEXT,
                    bio TEXT,
                    email_verification_token TEXT,
                    password_reset_token TEXT,
                    password_reset_expires TEXT
                )
            ''')
            
            # Login attempts table (for rate limiting)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS login_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    ip_address TEXT,
                    attempt_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT 0
                )
            ''')
            
            # User sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # Admin logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    target_user_id INTEGER,
                    ip_address TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    details TEXT,
                    FOREIGN KEY (admin_id) REFERENCES users(id),
                    FOREIGN KEY (target_user_id) REFERENCES users(id)
                )
            ''')
            
            # Chat history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            conn.close()
    
    # ============ USER OPERATIONS ============
    
    def create_user(self, name: str, email: str, password: str, role: str = "user") -> Optional[User]:
        """Create new user"""
        try:
            password_hash = PasswordManager.hash_password(password)
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (name, email, password_hash, role))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            return self.get_user_by_id(user_id)
        except sqlite3.IntegrityError:
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM users WHERE id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_user(row)
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM users WHERE email = ?
            ''', (email.lower(),))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_user(row)
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user"""
        try:
            allowed_fields = {'name', 'bio', 'profile_picture', 'last_login', 'email_verified', 'is_active', 'password_hash'}
            updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not updates:
                return self.get_user_by_id(user_id)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
            values = list(updates.values()) + [user_id]
            
            cursor.execute(f'''
                UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', values)
            
            conn.commit()
            conn.close()
            
            return self.get_user_by_id(user_id)
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        try:
            password_hash = PasswordManager.hash_password(new_password)
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (password_hash, user_id))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False
    
    def get_all_users(self, role: Optional[str] = None) -> List[User]:
        """Get all users (admin only)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if role:
                cursor.execute('SELECT * FROM users WHERE role = ?', (role,))
            else:
                cursor.execute('SELECT * FROM users')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_user(row) for row in rows]
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user (admin only)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete related data first
            cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    # ============ LOGIN ATTEMPTS (Rate Limiting) ============
    
    def record_login_attempt(self, email: str, ip_address: str, success: bool) -> None:
        """Record login attempt"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO login_attempts (email, ip_address, success)
                VALUES (?, ?, ?)
            ''', (email.lower(), ip_address, success))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error recording login attempt: {e}")
    
    def get_recent_login_attempts(self, email: str, minutes: int = 15) -> int:
        """Get count of failed login attempts in last N minutes"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM login_attempts
                WHERE email = ? AND success = 0
                AND datetime(attempt_time) > datetime('now', '-' || ? || ' minutes')
            ''', (email.lower(), minutes))
            
            result = cursor.fetchone()
            conn.close()
            
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting login attempts: {e}")
            return 0
    
    # ============ SESSIONS ============
    
    def create_session(self, user_id: int, session_token: str, ip_address: str, user_agent: str, expires_at: str) -> bool:
        """Create user session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (user_id, session_token, ip_address, user_agent, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, session_token, ip_address, user_agent, expires_at))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    def get_session(self, session_token: str) -> Optional[Dict]:
        """Get session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM sessions WHERE session_token = ? AND is_active = 1
            ''', (session_token,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            return None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    def destroy_session(self, session_token: str) -> bool:
        """Destroy session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions SET is_active = 0 WHERE session_token = ?
            ''', (session_token,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error destroying session: {e}")
            return False
    
    # ============ ADMIN LOGS ============
    
    def log_admin_action(self, admin_id: int, action: str, target_user_id: Optional[int], ip_address: str, details: Optional[str]) -> None:
        """Log admin action"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO admin_logs (admin_id, action, target_user_id, ip_address, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (admin_id, action, target_user_id, ip_address, details))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging admin action: {e}")
    
    # ============ CHAT HISTORY ============
    
    def save_chat_message(self, user_id: int, session_id: str, message: str, response: str) -> bool:
        """Save chat message to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO chat_history (user_id, session_id, message, response)
                VALUES (?, ?, ?, ?)
            ''', (user_id, session_id, message, response))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error saving chat message: {e}")
            return False
    
    def get_chat_history(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Get chat history for user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_id, message, response, timestamp
                FROM chat_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
    
    def delete_chat_history(self, user_id: int) -> bool:
        """Delete all chat history for user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM chat_history WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error deleting chat history: {e}")
            return False
    
    def get_all_chat_history(self) -> List[Dict]:
        """Get all chat history (admin only)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_id, message, response, timestamp
                FROM chat_history
                ORDER BY timestamp DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting all chat history: {e}")
            return []
    
    # ============ UTILITY METHODS ============
    
    def _row_to_user(self, row) -> User:
        """Convert database row to User object"""
        return User(
            id=row['id'],
            name=row['name'],
            email=row['email'],
            password_hash=row['password_hash'],
            is_active=bool(row['is_active']),
            email_verified=bool(row['email_verified']),
            role=row['role'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            last_login=row['last_login'],
            profile_picture=row['profile_picture'],
            bio=row['bio']
        )


# Global database instance
db = Database()
