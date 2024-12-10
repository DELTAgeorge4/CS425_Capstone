from backend.db.main import connect, close

def Get_Honeypot_Info():
#    authenticated = False
    conn, cur = connect()
    cur.execute("SELECT * FROM honeypot")
    result = cur.fetchall()
    close(conn, cur)
    return result
