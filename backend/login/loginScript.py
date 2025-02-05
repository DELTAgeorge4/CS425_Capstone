from backend.db.main import connect, close
from backend.passwordHashing.hashmypassword import hash_password

def login(username, password):
    authenticated = False
    conn, cur = connect()
    cur.execute("SELECT password_hash, salt FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    close(conn, cur)
    print(result)
    if not result:
        print(f"Username '{username}' does not exist.")
        return authenticated

    hashed_password, salty = result
    
    if hash_password(password, salty)[0] == hashed_password:
        print(f"User '{username}' logged in successfully!")
        authenticated = True
    else:
        print(f"Invalid password for user '{username}'")
        
    return authenticated
        
def getUserRole(username):
    conn, cur = connect()
    try: 
        cur.execute("SELECT role FROM users WHERE username = %s;", (username,))
        result = cur.fetchone()
        role = result[0]
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        close(conn,cur)
        
    print(role)
    print(type(role))
    return role