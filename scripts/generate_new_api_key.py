"""
Generate a new API key and replace the exposed one.
Run this to create a fresh, secure API key for your SDK.
"""
import sys
import os
sys.path.append('../alinea-ai')

from app.utils.auth import generate_api_key
from app.db.connection import get_db

def create_new_api_key():
    """Generate and store a new API key."""
    print("🔑 Generating new API key...")
    
    # Generate new key
    new_key = generate_api_key()
    print(f"New key: {new_key}")
    
    # Update database
    with get_db() as conn:
        # Update existing user or create new one
        conn.execute(
            "UPDATE users SET api_key = ? WHERE email = ?",
            (new_key, "scale-test@alinea.ai")
        )
        
        # If no update happened, insert new user
        if conn.rowcount == 0:
            conn.execute(
                "INSERT INTO users (email, api_key) VALUES (?, ?)",
                ("your-email@example.com", new_key)
            )
        
        conn.commit()
    
    print("✅ API key updated in database")
    print(f"🔐 Your new secure API key: {new_key}")
    print("\n🛡️ Keep this key secure and private!")
    
    return new_key

if __name__ == "__main__":
    create_new_api_key()