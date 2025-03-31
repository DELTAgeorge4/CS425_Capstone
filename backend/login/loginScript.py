from backend.db.main import connect, close
from backend.passwordHashing.hashmypassword import hash_password

def login(username, password):
    authenticated = False
    conn, cur = connect()
    cur.execute("SELECT password_hash, salt FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    close(conn, cur)
    # print(result)
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
        
def getUserID(username):
    conn, cur = connect()
    try: 
        cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
        result = cur.fetchone()
        userID = result[0]
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        close(conn,cur)
        
    return userID



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

#function for every user(including admins) to change their own passwords
def changePassword(username, oldPassword, newPassword):
    canChange = login(username, oldPassword)
    
    if (canChange):
        newHashedPassword, newSalt = hash_password(newPassword)
        conn, cur = connect()
        
        try:
                # Update password hash and salt
            cur.execute("""UPDATE users SET password_hash = %s, salt = %s WHERE username = %s; """, (newHashedPassword, newSalt, username))

            # Commit the changes
            conn.commit()
        except psycopg2.Error as e:
            print(f"Error: {e}")
        finally:
            close(conn, cur)
        return True
    else:
        return False
    
#function for admin to change passwords of other users 
def resetPassword(adminUsername, userUsername, newPassword):
    userRole = getUserRole(adminUsername)
    isAdmin = (userRole == "admin")
    
    if isAdmin:
        newHashedPassword, newSalt = hash_password(newPassword)
        conn, cur = connect()
        
        try:
                # Update password hash and salt
            cur.execute("""UPDATE users SET password_hash = %s, salt = %s WHERE username = %s; """, (newHashedPassword, newSalt, userUsername))

            # Commit the changes
            conn.commit()
        except psycopg2.Error as e:
            print(f"Error: {e}")
        finally:
            close(conn, cur)
            
        return True
    else:
        return False
    
def getUsers():
    conn, cur = connect()
    try: 
        cur.execute("SELECT username, role FROM users;")
        result = cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        close(conn,cur)
        
    return result