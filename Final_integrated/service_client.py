"""
Service Client Module

This module provides client functions to interact with all microservices:
- Session Management Service
- Activity Logs Service
- Auth Service
- Feedback Service
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Service URLs (with default values)
SESSION_SERVICE_URL = os.getenv("SESSION_SERVICE_URL", "http://localhost:8003")
ACTIVITY_LOGS_SERVICE_URL = os.getenv("ACTIVITY_LOGS_SERVICE_URL", "http://localhost:8000")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5000/api")
FEEDBACK_SERVICE_URL = os.getenv("FEEDBACK_SERVICE_URL", "http://localhost:5003")

class AuthClient:
    """Client for interacting with the Authentication Service"""
    
    @staticmethod
    def register(name, email, password, role="user"):
        """Register a new user"""
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/register",
            json={
                "name": name,
                "email": email,
                "password": password,
                "role": role
            }
        )
        return response.json() if response.status_code in [200, 201] else None
    
    @staticmethod
    def login(email, password):
        """Login a user and get user data with token"""
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            }
        )
        return response.json() if response.status_code != 500 else None

class SessionClient:
    """Client for interacting with the Session Management Service"""
    
    @staticmethod
    def create_token(username):
        """Create access and refresh tokens for a user"""
        response = requests.post(
            f"{SESSION_SERVICE_URL}/token",
            json={"username": username}
        )
        return response.json() if response.status_code == 200 else None
    
    @staticmethod
    def refresh_token(refresh_token):
        """Refresh an access token"""
        response = requests.post(
            f"{SESSION_SERVICE_URL}/refresh",
            json={"refresh_token": refresh_token}
        )
        return response.json() if response.status_code == 200 else None
    
    @staticmethod
    def get_status(access_token):
        """Get session status"""
        response = requests.get(
            f"{SESSION_SERVICE_URL}/status",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    
    @staticmethod
    def update_activity(access_token):
        """Update user's activity timestamp"""
        response = requests.post(
            f"{SESSION_SERVICE_URL}/activity",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json() if response.status_code == 200 else None
    
    @staticmethod
    def logout(access_token):
        """Log out a user by blacklisting their token"""
        response = requests.post(
            f"{SESSION_SERVICE_URL}/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json() if response.status_code == 200 else None

class ActivityLogClient:
    """Client for interacting with the Activity Logs Service"""
    
    @staticmethod
    def record_log(level, component, message, user_id=None, ip_address=None, action=None, resource=None, details=None):
        """Record an activity log"""
        log_data = {
            "level": level,
            "component": component,
            "message": message,
            "user_id": user_id,
            "ip_address": ip_address,
            "action": action,
            "resource": resource,
            "details": details
        }
        
        response = requests.post(
            f"{ACTIVITY_LOGS_SERVICE_URL}/logs/record",
            json=log_data
        )
        return response.json() if response.status_code == 200 else None
    
    @staticmethod
    def get_user_logs(user_id, limit=100, skip=0):
        """Get logs for a specific user"""
        response = requests.get(
            f"{ACTIVITY_LOGS_SERVICE_URL}/logs/user/{user_id}",
            params={"limit": limit, "skip": skip}
        )
        return response.json() if response.status_code == 200 else None
    
    @staticmethod
    def get_system_logs(level=None, limit=100, skip=0):
        """Get system logs with optional filtering by level"""
        params = {"limit": limit, "skip": skip}
        if level:
            params["level"] = level
            
        response = requests.get(
            f"{ACTIVITY_LOGS_SERVICE_URL}/logs/system",
            params=params
        )
        return response.json() if response.status_code == 200 else None
    
    @staticmethod
    def get_auth_logs(limit=100, skip=0):
        """Get authentication logs"""
        response = requests.get(
            f"{ACTIVITY_LOGS_SERVICE_URL}/logs/auth",
            params={"limit": limit, "skip": skip}
        )
        return response.json() if response.status_code == 200 else None

class FeedbackClient:
    """Client for interacting with the Feedback Service"""
    
    @staticmethod
    def submit_feedback(access_token, message):
        """Submit feedback"""
        response = requests.post(
            f"{FEEDBACK_SERVICE_URL}/feedback",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message": message}
        )
        return response.json()
    
    @staticmethod
    def get_all_feedback(access_token):
        """Get all feedback submissions (admin only)"""
        response = requests.get(
            f"{FEEDBACK_SERVICE_URL}/feedback",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json() 

class IntegratedServices:
    """Class for integrated microservice operations"""
    
    def __init__(self):
        self.auth = AuthClient()
        self.session = SessionClient()
        self.activity = ActivityLogClient()
        self.feedback = FeedbackClient()
        
        # Current user session data
        self.current_user = None
        self.tokens = None
    
    def register_user(self, name, email, password, role="user"):
        """Register a new user"""
        user_data = self.auth.register(name, email, password, role)
        
        if user_data:
            self.activity.record_log(
                level="INFO",
                component="auth.register",
                message=f"User {email} registered",
                user_id=user_data.get("_id"),
                action="REGISTER",
                resource="auth"
            )
            
        return user_data
    
    def login_user(self, email, password):
        """Login a user and set up their session"""
        # 1. Authenticate with Auth Service
        auth_data = self.auth.login(email, password)
        
        if not auth_data:
            print("hello",auth_data)
            return False
        
        # 2. Create session tokens
        print(auth_data.get("user"))
        self.current_user = auth_data.get("user")
        token_data = self.session.create_token(email)
        
        if not token_data:
            print(token_data)
            return False
        
        self.tokens = token_data
        
        # 3. Log the login activity
        self.activity.record_log(
            level="INFO",
            component="auth.login",
            message=f"User {email} logged in",
            user_id=self.current_user.get("_id"),
            action="LOGIN",
            resource="auth"
        )
        
        return True
    
    def submit_user_feedback(self, message):
        """Submit feedback from the current user"""
        if not self.current_user or not self.tokens:
            print("hello",self.current_user)
            return False
        
        result = self.feedback.submit_feedback(
            self.tokens.get("access_token"),
            message
        )
        print(result)
        if result:
            self.activity.record_log(
                level="INFO",
                component="feedback.submit",
                message="User submitted feedback",
                user_id=self.current_user.get("_id"),
                action="SUBMIT_FEEDBACK",
                resource="feedback"
            )
            
            # Update user activity
            self.session.update_activity(self.tokens.get("access_token"))
            return True
            
        return False
    
    def get_user_activity(self, limit=10):
        """Get the current user's activity logs"""
        if not self.current_user or not self.tokens:
            return None
        
        # Update user activity
        self.session.update_activity(self.tokens.get("access_token"))
        
        # Get user logs
        return self.activity.get_user_logs(
            self.current_user.get("_id"),
            limit=limit
        )
    
    def get_all_feedback(self):
        """Get all feedback (admin only)"""
        if not self.current_user or not self.tokens:
            return None
            
        if self.current_user.get("role") != "admin":
            return {"error": "Admin access required"}
            
        # Update user activity
        self.session.update_activity(self.tokens.get("access_token"))
        
        return self.feedback.get_all_feedback(self.tokens.get("access_token"))
    
    def refresh_session(self):
        """Refresh the current session"""
        if not self.tokens or "refresh_token" not in self.tokens:
            return False
            
        new_tokens = self.session.refresh_token(self.tokens.get("refresh_token"))
        
        if new_tokens:
            self.tokens["access_token"] = new_tokens.get("access_token")
            return True
            
        return False
    
    def logout(self):
        """Log out the current user"""
        if not self.current_user or not self.tokens:
            return False
            
        # Log the activity first (before we invalidate the token)
        self.activity.record_log(
            level="INFO", 
            component="auth.logout",
            message=f"User {self.current_user.get('email')} logged out",
            user_id=self.current_user.get("_id"),
            action="LOGOUT",
            resource="auth"
        )
        
        # Logout with session service
        result = self.session.logout(self.tokens.get("access_token"))
        
        if result:
            self.current_user = None
            self.tokens = None
            return True
            
        return False