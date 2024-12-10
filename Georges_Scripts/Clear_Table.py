import psycopg2
from psycopg2 import sql
import config
import argparse

# Global Database Configuration
DB_HOST = config.DB_HOST
DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run the database script with dynamic configurations.")
parser.add_argument(
    "--tables", 
    nargs="*", 
    default=["snmp_metrics"], 
    help="List of tables to include. Example: --tables table1 table2"
)
args = parser.parse_args()

# Use tables from command-line arguments
TABLES = args.tables

def get_db_connection():
    # Establishes and returns a database connection using global configurations.
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )

def clear_table(table_name):
    connection = None
    cursor = None
    try:
        # Get a database connection
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Use SQL injection-safe query to truncate the table
        query = sql.SQL("TRUNCATE TABLE {table} RESTART IDENTITY CASCADE").format(
            table=sql.Identifier(table_name)
        )
        cursor.execute(query)
        connection.commit()
        #print(f"Table '{table_name}' cleared successfully.")
    
    except psycopg2.Error as e:
        print(f"Error: {e}")
    
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Example usage
if __name__ == "__main__":
    for table in TABLES:
        clear_table(table)
