#login.signup.py
from db.main import connect, close, usernameExists
from passwordHashing.hashmypassword import hash_password

def create_user(username, password):
    if usernameExists(username):
        print(f"Username '{username}' already exists.")
        return
    conn, cur = connect()
    hashed_password, salty = hash_password(password)
    cur.execute("INSERT INTO users (username, password_hash, salt) VALUES (%s, %s, %s)", (username, hashed_password, salty))
    conn.commit()
    close(conn, cur)
    print(f"User '{username}' created successfully!")
    
create_user("admin", "admin")