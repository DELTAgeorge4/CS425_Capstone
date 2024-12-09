#db.main
import psycopg2

# Function to check if a username exists
def usernameExists(username):
    conn, cur = connect()
    try:
        cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        return result is not None  # Return True if username exists, False otherwise
    except psycopg2.Error as e:
        print(f"Error querying username: {e}")
        return False
    finally:
        close(conn, cur)

def connect():
    try:
        conn = psycopg2.connect(
            dbname="nss",  # Ensure this matches your database name
            user="postgres",
            password="password123",  # Use the password you set
            host="localhost"
        )
        cur = conn.cursor()
        return conn, cur
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise SystemExit("Database connection failed.")


# Function to close the database connection
def close(conn, cur):
    try:
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error closing the database connection: {e}")
        
        
        
def test_connection():
    conn, cur = connect()
    try:
        cur.execute("SELECT 1;")
        print("Connection successful!")
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        close(conn, cur)

# Call the test function
test_connection()
