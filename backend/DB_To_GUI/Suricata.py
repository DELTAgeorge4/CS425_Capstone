from backend.db.main import connect, close

def Get_Suricata_Info():
#    authenticated = False
    conn, cur = connect()
    cur.execute("SELECT * FROM suricata")
    result = cur.fetchall()
    close(conn, cur)
    return result
