from backend.db.main import connect, close

def Get_SNMP_Info():
#    authenticated = False
    conn, cur = connect()
    cur.execute("SELECT * FROM snmp_metrics")
    result = cur.fetchall()
    close(conn, cur)
    return result
