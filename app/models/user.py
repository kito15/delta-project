from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app, g
from app import get_db

class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, id=None, username=None, email=None, password_hash=None, 
                 created_at=None, updated_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.updated_at = updated_at

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    def save(self):
        """Save user to database (INSERT or UPDATE)"""
        db = get_db()
        cursor = db.cursor()
        
        try:
            if self.id is None:
                # INSERT new user
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (self.username, self.email, self.password_hash, 
                      datetime.utcnow(), datetime.utcnow()))
                self.id = cursor.lastrowid
            else:
                # UPDATE existing user
                cursor.execute("""
                    UPDATE users 
                    SET username = %s, email = %s, password_hash = %s, updated_at = %s
                    WHERE id = %s
                """, (self.username, self.email, self.password_hash, 
                      datetime.utcnow(), self.id))
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    def delete(self):
        """Delete user from database"""
        if self.id is None:
            return False
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute("DELETE FROM users WHERE id = %s", (self.id,))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        db = get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, email, password_hash, created_at, updated_at
                FROM users WHERE id = %s
            """, (user_id,))
            row = cursor.fetchone()
            
            if row:
                return cls(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
            return None
        finally:
            cursor.close()

    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        db = get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, email, password_hash, created_at, updated_at
                FROM users WHERE email = %s
            """, (email,))
            row = cursor.fetchone()
            
            if row:
                return cls(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
            return None
        finally:
            cursor.close()

    @classmethod
    def get_by_username(cls, username):
        """Get user by username"""
        db = get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, email, password_hash, created_at, updated_at
                FROM users WHERE username = %s
            """, (username,))
            row = cursor.fetchone()
            
            if row:
                return cls(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
            return None
        finally:
            cursor.close()

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'
