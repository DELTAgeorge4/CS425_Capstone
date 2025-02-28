#login.signup.py
from backend.db.main import connect, close, usernameExists
from backend.passwordHashing.hashmypassword import hash_password

def create_user(username, password, role):
    if usernameExists(username):
        print(f"Username '{username}' already exists.")
        return False
    conn, cur = connect()
    hashed_password, salty = hash_password(password)
    cur.execute("INSERT INTO users (username, password_hash, salt, role) VALUES (%s, %s, %s,%s)", (username, hashed_password, salty, role))
    conn.commit()
    close(conn, cur)
    # print(f"User '{username}' created successfully!")
    return True
    
    
def check_role_exists(role):
    conn, cur = connect()
    cur.execute("SELECT * FROM users WHERE role = %s", (role,))
    result = cur.fetchone()
    close(conn, cur)
    return result is not None


    

#command to run sign up  PYTHONPATH=./backend python3 -m login.signUp
if __name__ == "__main__":
    create_user("guest", "guest", "guest")
