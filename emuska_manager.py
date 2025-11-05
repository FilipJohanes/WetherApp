#!/usr/bin/env python3
"""
Emuska Mode Activation Script

This script demonstrates how to manually activate the secret "Emuska" personality mode
for specific users, since this mode cannot be set through email commands.
"""

import sqlite3
from datetime import datetime

def activate_emuska_mode(email: str, confirm: bool = False):
    """Activate Emuska mode for a specific user."""
    if not confirm:
        print("⚠️  This will change the user's personality mode to 'emuska'")
        print(f"   Email: {email}")
        print("   This is a SECRET mode - use carefully!")
        response = input("   Continue? (yes/no): ").lower().strip()
        if response not in ['yes', 'y']:
            print("❌ Cancelled.")
            return False
    
    conn = sqlite3.connect("app.db")
    try:
        # Check if user exists
        user = conn.execute("SELECT email, location, personality FROM subscribers WHERE email = ?", (email,)).fetchone()
        
        if not user:
            print(f"❌ User {email} not found in subscribers database.")
            return False
        
        old_personality = user[2] if user[2] else 'neutral'
        
        # Update to Emuska mode
        conn.execute("""
            UPDATE subscribers 
            SET personality = 'emuska', updated_at = ?
            WHERE email = ?
        """, (datetime.now().isoformat(), email))
        
        conn.commit()
        
        print(f"✅ Successfully activated Emuska mode for {email}")
        print(f"   Previous mode: {old_personality} → New mode: emuska")
        print(f"   Location: {user[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        conn.close()

def list_emuska_users():
    """List all users currently using Emuska mode."""
    conn = sqlite3.connect("app.db")
    try:
        emuska_users = conn.execute("""
            SELECT email, location, updated_at 
            FROM subscribers 
            WHERE personality = 'emuska'
            ORDER BY updated_at DESC
        """).fetchall()
        
        if emuska_users:
            print(f"👑 Found {len(emuska_users)} Emuska mode users:")
            for email, location, updated_at in emuska_users:
                print(f"   • {email} -> {location} (activated: {updated_at})")
        else:
            print("📭 No users currently using Emuska mode.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def deactivate_emuska_mode(email: str, new_mode: str = 'neutral'):
    """Deactivate Emuska mode for a user."""
    if new_mode not in ['neutral', 'cute', 'brutal']:
        print(f"❌ Invalid personality mode: {new_mode}")
        return False
    
    conn = sqlite3.connect("app.db")
    try:
        # Update personality mode
        cursor = conn.execute("""
            UPDATE subscribers 
            SET personality = ?, updated_at = ?
            WHERE email = ? AND personality = 'emuska'
        """, (new_mode, datetime.now().isoformat(), email))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Deactivated Emuska mode for {email} -> switched to {new_mode}")
            return True
        else:
            print(f"❌ User {email} was not using Emuska mode.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🌟 Emuska Mode Management 🌟")
    print()
    
    while True:
        print("Options:")
        print("1. Activate Emuska mode for user")
        print("2. List Emuska users") 
        print("3. Deactivate Emuska mode")
        print("4. Exit")
        print()
        
        choice = input("Choose option (1-4): ").strip()
        
        if choice == '1':
            email = input("Enter user email: ").strip()
            if email:
                activate_emuska_mode(email)
        elif choice == '2':
            list_emuska_users()
        elif choice == '3':
            email = input("Enter user email: ").strip()
            mode = input("New personality mode (neutral/cute/brutal): ").strip()
            if email and mode:
                deactivate_emuska_mode(email, mode)
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice.")
        
        print()