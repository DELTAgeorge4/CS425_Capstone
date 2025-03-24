from backend.db.main import connect, close

def get_theme(user_id):
    conn, cur = connect()
    try:
        cur.execute("SELECT theme FROM user_settings WHERE user_id = %s;", (user_id,))
        result = cur.fetchone()
        theme = result[0]
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        close(conn, cur)
    return theme

def set_theme(user_id , theme):
    conn, cur = connect()
    try:
        cur.execute("UPDATE user_settings SET theme = %s WHERE user_id = %s;", (theme, user_id))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        close(conn, cur)
    return True

def set_font_size(user_id, font_size):
    conn, cur = connect()
    try:
        cur.execute("UPDATE user_settings SET font_size = %s WHERE user_id = %s;", (font_size, user_id))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        close(conn, cur)
    return True


def get_font_size(user_id):
    conn, cur = connect()
    try:
        cur.execute("SELECT font_size FROM user_settings WHERE user_id = %s;", (user_id,))
        result = cur.fetchone()
        font_size = result[0]
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        close(conn, cur)
    return font_size
    
    
def set_default_settings(user_id):
    conn, cur = connect()
    try:
        cur.execute("UPDATE user_settings SET theme = 'light', font_size = 'medium' WHERE user_id = %s;", (user_id,))
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        close(conn, cur)
    return True


