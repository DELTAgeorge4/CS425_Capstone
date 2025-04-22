from backend.db.main import connect, close
from backend.passwordHashing.hashmypassword import hash_password
import psycopg2  # Added import for the error handling
import datetime

def log_to_db(username, action):
    conn, cur = connect()
    try:
        # Insert the log entry into the user_login_logs table (using our new table)
        cur.execute("INSERT INTO user_login_logs (username, action) VALUES (%s, %s);", (username, action))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error logging action: {e}")
    finally:
        close(conn, cur)
       
       
def get_recent_failed_attempts(username, minutes=30):
    conn, cur = connect()
    try:
        cur.execute("""
            SELECT COUNT(*) 
            FROM user_login_logs 
            WHERE username = %s 
            AND action = 'LOGIN_FAILED' 
            AND timestamp > NOW() - INTERVAL '%s minutes'
        """, (username, minutes))
        
        count = cur.fetchone()[0]
        return count
    except psycopg2.Error as e:
        print(f"Error counting failed login attempts: {e}")
        return 0
    finally:
        close(conn, cur)
       
def fetch_all_login_logs():
    conn, cur = connect()
    try:
        cur.execute("SELECT * FROM user_login_logs ORDER BY timestamp DESC LIMIT 10;")
        records = cur.fetchall()
        
        column_names = [desc[0] for desc in cur.description]
        
        logs = []
        for record in records:
            log_dict = {}
            for i, value in enumerate(record):
                if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                    log_dict[column_names[i]] = value.isoformat()
                elif isinstance(value, datetime.timedelta):
                    log_dict[column_names[i]] = str(value)
                else:
                    log_dict[column_names[i]] = value
            logs.append(log_dict)
            
        return logs
    except psycopg2.Error as e:
        print(f"Error fetching logs: {e}")
        return []  
    finally:
        close(conn, cur)

def login(username, password):
    authenticated = False
    conn, cur = connect()
    cur.execute("SELECT password_hash, salt FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    close(conn, cur)
    # print(result)
    if not result:
        print(f"Username '{username}' does not exist.")
        # Log failed login attempt
        log_to_db(username, "LOGIN_FAILED")
        return authenticated
    hashed_password, salty = result
   
    if hash_password(password, salty)[0] == hashed_password:
        print(f"User '{username}' logged in successfully!")
        # Log successful login
        log_to_db(username, "LOGGED_IN")
        authenticated = True
    else:
        print(f"Invalid password for user '{username}'")
        # Log failed login attempt
        log_to_db(username, "LOGIN_FAILED")
       
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
            # Log password change
            log_to_db(username, "PASSWORD_CHANGED")
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
            # Log password reset action
            log_to_db(adminUsername, f"RESET_PASSWORD_FOR_{userUsername}")
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

# Add a logout function to log when users log out
def logout(username):
    log_to_db(username, "LOGGED_OUT")
    print(f"User '{username}' logged out successfully!")
    return True