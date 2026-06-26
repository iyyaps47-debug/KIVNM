import re
from typing import Tuple, List
from email_validator import validate_email, EmailNotValidError
from config import (
    MIN_PASSWORD_LENGTH,
    REQUIRE_UPPERCASE,
    REQUIRE_LOWERCASE,
    REQUIRE_DIGITS,
    REQUIRE_SPECIAL_CHARS
)


class EmailValidator:
    """Validate email format and check for common issues"""
    
    @staticmethod
    def validate(email: str) -> Tuple[bool, str]:
        """
        Validate email address
        Args:
            email: Email address to validate
        Returns:
            Tuple of (is_valid, message)
        """
        if not email:
            return False, "Email is required"
        
        if len(email) > 255:
            return False, "Email is too long (max 255 characters)"
        
        try:
            # Validate and normalize email
            valid = validate_email(email)
            email = valid.email
            return True, "Email is valid"
        except EmailNotValidError as e:
            return False, str(e)
    
    @staticmethod
    def is_disposable_email(email: str) -> bool:
        """
        Check if email is from a disposable email provider
        Args:
            email: Email address
        Returns:
            True if disposable email
        """
        disposable_domains = {
            "tempmail.com", "guerrillamail.com", "10minutemail.com",
            "mailinator.com", "throwaway.email", "yopmail.com"
        }
        
        domain = email.split("@")[1].lower()
        return domain in disposable_domains
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalize email address
        Args:
            email: Email address
        Returns:
            Normalized email
        """
        return email.lower().strip()


class PasswordValidator:
    """Validate password strength"""
    
    @staticmethod
    def validate(password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength
        Args:
            password: Password to validate
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        if not password:
            return False, ["Password is required"]
        
        if len(password) < MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long")
        
        if REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if REQUIRE_DIGITS and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*)")
        
        # Check for common weak passwords
        weak_passwords = {
            "password", "123456", "qwerty", "abc123", "password123",
            "admin", "letmein", "welcome", "monkey"
        }
        
        if password.lower() in weak_passwords:
            errors.append("This password is too common. Please choose a stronger password")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def get_password_strength(password: str) -> str:
        """
        Get password strength rating
        Args:
            password: Password to rate
        Returns:
            Strength rating: 'weak', 'fair', 'good', 'strong', 'very-strong'
        """
        if not password:
            return "weak"
        
        score = 0
        
        if len(password) >= MIN_PASSWORD_LENGTH:
            score += 1
        if len(password) >= 12:
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            score += 1
        
        if score <= 2:
            return "weak"
        elif score == 3:
            return "fair"
        elif score == 4:
            return "good"
        elif score == 5:
            return "strong"
        else:
            return "very-strong"
    
    @staticmethod
    def check_password_breach(password: str) -> Tuple[bool, str]:
        """
        Check if password has been breached using Have I Been Pwned API
        Args:
            password: Password to check
        Returns:
            Tuple of (is_breached, message)
        """
        try:
            import hashlib
            import requests
            
            # Only check first 5 characters of SHA1 hash
            sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
            prefix = sha1_hash[:5]
            
            # Query HIBP API
            response = requests.get(
                f"https://api.pwnedpasswords.com/range/{prefix}",
                timeout=2
            )
            
            if response.status_code != 200:
                return False, "Unable to check password breach status"
            
            # Check if our hash is in the response
            hashes = response.text.split('\r\n')
            for line in hashes:
                if line.startswith(sha1_hash[5:]):
                    return True, "This password has been found in data breaches. Please use a different password"
            
            return False, "Password not found in breach database"
        except Exception as e:
            # If API is unreachable, allow password but log warning
            return False, "Could not verify password against breach database"


class NameValidator:
    """Validate user names"""
    
    @staticmethod
    def validate(name: str) -> Tuple[bool, str]:
        """
        Validate user name
        Args:
            name: User name to validate
        Returns:
            Tuple of (is_valid, message)
        """
        if not name or not name.strip():
            return False, "Name is required"
        
        if len(name) < 2:
            return False, "Name must be at least 2 characters long"
        
        if len(name) > 100:
            return False, "Name must not exceed 100 characters"
        
        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, "Name is valid"
