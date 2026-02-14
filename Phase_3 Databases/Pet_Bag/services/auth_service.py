# services/auth_service.py
# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Authentication service for user login/logout and password management

import hashlib
from datetime import datetime

class AuthService:
    @staticmethod
    # authenticate user with username and password
    def authenticate_user(db, username, password):
        
        try:
            cursor = db.connection.cursor(dictionary=True)
            
            # get user by username
            cursor.execute("""
                SELECT user_id, username, password_hash, email, first_name, last_name, is_active
                FROM Users 
                WHERE username = %s AND is_active = TRUE
            """, (username,))
            
            user = cursor.fetchone()
            cursor.close()
            
            if not user:
                return None, "Invalid username or account is inactive"
            
            # verify password 
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] == password_hash:
                # update last login time
                cursor = db.connection.cursor()
                cursor.execute("""
                    UPDATE Users 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE user_id = %s
                """, (user['user_id'],))
                db.connection.commit()
                cursor.close()
                
                return user, "Login successful"
            else:
                return None, "Invalid password"
                
        except Exception as e:
            return None, f"Authentication error: {str(e)}"
    
    @staticmethod
    # change user password
    def change_password(db, user_id, current_password, new_password, confirm_password):
        
        try:
            # validate inputs
            if not current_password or not new_password:
                return False, "All fields are required"
            
            if new_password != confirm_password:
                return False, "New passwords do not match"
            
            if len(new_password) < 6:
                return False, "Password must be at least 6 characters"
            
            # get current password hash
            cursor = db.connection.cursor(dictionary=True)
            cursor.execute("SELECT password_hash FROM Users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            
            if not user:
                return False, "User not found"
            
            # verify current password
            current_hash = hashlib.sha256(current_password.encode()).hexdigest()
            if user['password_hash'] != current_hash:
                return False, "Current password is incorrect"
            
            # update password
            new_hash = hashlib.sha256(new_password.encode()).hexdigest()
            cursor = db.connection.cursor()
            cursor.execute("""
                UPDATE Users 
                SET password_hash = %s, password_changed_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (new_hash, user_id))
            db.connection.commit()
            cursor.close()
            
            return True, "Password changed successfully"
            
        except Exception as e:
            return False, f"Password change error: {str(e)}"
    
    @staticmethod
    # clear user session
    def logout_user():
        
        return True, "Logged out successfully"