#!/usr/bin/env python3
"""
Script to promote a user to admin status.
Usage: python make_admin.py user@example.com
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def make_admin(email):
    """Promote a user to admin status by email"""
    # Get database URL from environment
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Parse connection parameters
    result = urlparse(db_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    
    # Connect to database
    try:
        conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # First check if user exists
        cursor.execute("SELECT id, username, email, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"ERROR: No user found with email {email}")
            conn.close()
            sys.exit(1)
        
        user_id, username, user_email, role = user
        
        if role == 1:
            print(f"User {username} ({email}) is already an admin")
            conn.close()
            return
        
        # Update user to admin
        cursor.execute("UPDATE users SET role = 1 WHERE email = %s", (email,))
        print(f"SUCCESS: User {username} ({email}) has been promoted to admin")
        
        # Verify change
        cursor.execute("SELECT role FROM users WHERE email = %s", (email,))
        new_role = cursor.fetchone()[0]
        print(f"Verified new role: {'Admin' if new_role == 1 else 'Student'}")
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py user@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    make_admin(email)