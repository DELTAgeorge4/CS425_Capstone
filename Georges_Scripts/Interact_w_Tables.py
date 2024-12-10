import psycopg2
import config

# Global Database Connection Details
DB_HOST = config.DB_HOST
DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD

# Global List of Tables
TABLES = config.TESTING_TABLES  # Defines tables

# Establishes and returns a database connection
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )

# Displays the contents of the specified table
def show_table_contents(table_name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        print(f"Contents of '{table_name}':")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error while querying '{table_name}': {e}")
    finally:
        cursor.close()
        conn.close()

# Wipes all contents of the specified table after confirmation
def wipe_table(table_name):
    confirm = input(f"Would you like to wipe the table: '{table_name}'? (y/N): ")
    if confirm.lower() == 'y':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"TRUNCATE {table_name} RESTART IDENTITY;")
            conn.commit()
            print(f"Table '{table_name}' wiped.")
        except Exception as e:
            print(f"Error while wiping '{table_name}': {e}")
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    for table in TABLES:
        print(f"\nProcessing table: {table}")
        show_table_contents(table)
        wipe_table(table)
