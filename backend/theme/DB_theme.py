from backend.db.main import connect, close
import psycopg2

def get_theme(user_id):
    conn, cur = connect()
    theme = "light"  # Default theme
    try:
        cur.execute("SELECT theme FROM user_settings WHERE user_id = %s;", (user_id,))
        result = cur.fetchone()
        if result is not None:
            theme = result[0]
        else:
            # If no settings found, create them
            set_default_settings(user_id)
    except psycopg2.Error as e:
        print(f"Error getting theme: {e}")
    finally:
        close(conn, cur)
    return theme

def set_theme(user_id, theme):
    conn, cur = connect()
    try:
        # Check if user has settings
        cur.execute("SELECT 1 FROM user_settings WHERE user_id = %s;", (user_id,))
        if cur.fetchone() is None:
            # Create settings if they don't exist
            set_default_settings(user_id)
            
        # Now update the theme
        cur.execute("UPDATE user_settings SET theme = %s WHERE user_id = %s;", (theme, user_id))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error setting theme: {e}")
    finally:
        close(conn, cur)
    return True

def get_font_size(user_id):
    conn, cur = connect()
    font_size = "medium"  # Default font size
    try:
        cur.execute("SELECT font_size FROM user_settings WHERE user_id = %s;", (user_id,))
        result = cur.fetchone()
        if result is not None:
            font_size = result[0]
        else:
            # If no settings found, create them
            set_default_settings(user_id)
    except psycopg2.Error as e:
        print(f"Error getting font size: {e}")
    finally:
        close(conn, cur)
    return font_size

def set_font_size(user_id, font_size):
    conn, cur = connect()
    try:
        # Check if user has settings
        cur.execute("SELECT 1 FROM user_settings WHERE user_id = %s;", (user_id,))
        if cur.fetchone() is None:
            # Create settings if they don't exist
            set_default_settings(user_id)
            
        # Now update the font size
        cur.execute("UPDATE user_settings SET font_size = %s WHERE user_id = %s;", (font_size, user_id))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error setting font size: {e}")
    finally:
        close(conn, cur)
    return True

def set_default_settings(user_id):
    """Create or update default settings for a user"""
    conn, cur = connect()
    try:
        # First check if the user already has settings
        cur.execute("SELECT 1 FROM user_settings WHERE user_id = %s;", (user_id,))
        if cur.fetchone() is None:
            # INSERT new record if none exists
            cur.execute(
                "INSERT INTO user_settings (user_id, theme, font_size) VALUES (%s, 'light', 'medium');", 
                (user_id,)
            )
        else:
            # UPDATE existing record
            cur.execute(
                "UPDATE user_settings SET theme = 'light', font_size = 'medium' WHERE user_id = %s;", 
                (user_id,)
            )
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error setting default settings: {e}")
        return False
    finally:
        close(conn, cur)
    return True