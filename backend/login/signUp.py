#login.signup.py
from backend.db.main import connect, close, usernameExists
from backend.passwordHashing.hashmypassword import hash_password
from backend.theme.DB_theme import set_default_settings
from backend.login.loginScript import getUserID

def user_default_notifications(user_id):
    """Set default notification preferences for a new user."""
    conn, cur = connect()
    try:
        # Get all notification types 
        cur.execute("SELECT id FROM notification_types")
        notification_types = cur.fetchall()
        
        # Insert default preferences for each notification type
        for notification_type in notification_types:
            notification_type_id = notification_type[0]
            cur.execute("""
                INSERT INTO user_notification_preferences 
                (user_id, notification_type_id, email_enabled) 
                VALUES (%s, %s, %s)
            """, (user_id, notification_type_id, True))
        
        conn.commit()
        print(f"Default notification preferences set for user ID: {user_id}")
    except Exception as e:
        print(f"Error setting default notifications: {e}")
        conn.rollback()
    finally:
        close(conn, cur)
        

def create_user(username, email, password, role='user'):
    if usernameExists(username):
        print(f"Username '{username}' already exists.")
        return False
    
    conn, cur = connect()
    hashed_password, salty = hash_password(password)
    
    try:
        # Insert the new user
        cur.execute("""
            INSERT INTO users (username, password_hash, salt, role, email) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id
        """, (username, hashed_password, salty, role, email))
        
        # Get the new user's ID
        user_id = cur.fetchone()[0]
        conn.commit()
        
        # Close the first connection as your existing code does
        close(conn, cur)
        
        # Set default theme settings
        set_default_settings(user_id)
        
        # Set default notification preferences
        user_default_notifications(user_id)
        
        # print(f"User '{username}' created successfully!")
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        conn.rollback()
        close(conn, cur)
        return False
def check_role_exists(role):
    conn, cur = connect()
    cur.execute("SELECT * FROM users WHERE role = %s", (role,))
    result = cur.fetchone()
    close(conn, cur)
    return result is not None

def set_user_notification_preferences(user_id, notification_type, is_enabled):
    
    conn, cur = connect()
    try:

        cur.execute("""
            UPDATE user_notification_preferences unp
            SET email_enabled = %s, updated_at = CURRENT_TIMESTAMP
            FROM notification_types nt
            WHERE unp.notification_type_id = nt.id
              AND unp.user_id = %s 
              AND nt.type_name = %s
        """, (is_enabled, user_id, notification_type))
        
        # Check if any rows were updated
        if cur.rowcount == 0:
            print(f"No preference found for user {user_id} and notification type '{notification_type}'")
            return False
        
        conn.commit()
        print(f"Updated '{notification_type}' preference to {is_enabled} for user ID: {user_id}")
        return True
    except Exception as e:
        print(f"Error updating notification preference: {e}")
        conn.rollback()
        return False
    finally:
        close(conn, cur)

def get_user_notification_preferences(user_id):
    conn, cur = connect()
    try:
        cur.execute("""
            SELECT nt.type_name, unp.email_enabled
            FROM user_notification_preferences unp
            JOIN notification_types nt ON unp.notification_type_id = nt.id
            WHERE unp.user_id = %s
        """, (user_id,))
        preferences = cur.fetchall()
        return preferences
    except Exception as e:
        print(f"Error fetching notification preferences: {e}")
        return None
    finally:
        close(conn, cur)
        
# def set_user_notification_preferences(user_id, notification_type_id, email_enabled):
        
def delete_user(username):
    conn, cur = connect()
    try:
        cur.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        print(f"User '{username}' deleted successfully!")
    except psycopg2.Error as e: 
        print(f"Error deleting user '{username}': {e}")
    finally:
        close(conn, cur)
        
def change_user_role(username, new_role):
    conn, cur = connect()
    try:
        cur.execute("UPDATE users SET role = %s WHERE username = %s", (new_role, username))
        conn.commit()
        print(f"User '{username}' role changed to '{new_role}' successfully!")
    except psycopg2.Error as e:
        print(f"Error changing role for user '{username}': {e}")
    finally:
        close(conn, cur)
        
        


    

#command to run sign up  PYTHONPATH=./backend python3 -m login.signUp
if __name__ == "__main__":
    create_user("guest", "guest", "guest")
