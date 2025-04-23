#login.signup.py
from backend.db.main import connect, close, usernameExists
from backend.passwordHashing.hashmypassword import hash_password
from backend.theme.DB_theme import set_default_settings
from backend.login.loginScript import getUserID

def create_user(username, email, password, role):
    if usernameExists(username):
        print(f"Username '{username}' already exists.")
        return False
    conn, cur = connect()
    hashed_password, salty = hash_password(password)
    cur.execute("INSERT INTO users (username, password_hash, salt, role, email) VALUES (%s, %s, %s,%s, %s)", (username, hashed_password, salty, role, email))

    
    conn.commit()
    
    
    close(conn, cur)
    
    set_default_settings(getUserID(username))
    # print(f"User '{username}' created successfully!")
    return True
    
    
def check_role_exists(role):
    conn, cur = connect()
    cur.execute("SELECT * FROM users WHERE role = %s", (role,))
    result = cur.fetchone()
    close(conn, cur)
    return result is not None

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
