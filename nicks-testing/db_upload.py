import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

class Database:
    def __init__(self, dbname=None, user=None, password=None, host=None, port=None):
        self.conn = None
        self.cursor = None
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
    

    def connect(self):
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
    
    def execute(self, query, parameters=None):
        self.cursor = self.conn.cursor()
        self.cursor.execute(query, parameters)
        self.conn.commit()

    def get_query_result(self):
        return self.cursor.fetchall()

    def close_connection(self):
        self.conn.close()


class ethernet_packet:
    def __init__(self, database, raw_data=None, type=None, type_val=None, dest=None, source=None, protocol=None):
        self.database = database
        self.raw_data = raw_data
        self.type = type
        self.type_val = type_val
        self.dest = dest
        self.source = source
        self.datetime = None

    def upload_packet(self, packet):
        query = """
        INSERT INTO Link_Layer_Packet (
            protocol, 
            destination_mac, 
            source_mac, 
            network_packet_type, 
            raw_data, 
            timestamp
        ) VALUES (
            %s, 
            %s, 
            %s, 
            %s, 
            %s, 
            %s
        );
        """
        self.protocol = packet['protocol']
        self.dest = packet['destination_mac']
        self.source = packet['source_mac']
        self.type = packet['ethertype_meaning']
        self.raw_data = packet['raw_packet'] # needs to be handled as array
        self.datetime = datetime.now()

        params = (
            self.protocol,
            self.dest,
            self.source,
            self.type,
            self.raw_data,
            self.datetime
        )

        self.database.execute(query, params)



if __name__ == "__main__":
    load_dotenv('db_credentials.env')
    db_name = os.getenv('DATABASE_NAME')
    db_host = os.getenv('DATABASE_HOST')
    db_port = os.getenv('DATABASE_PORT')
    db_user = os.getenv('DATABASE_USER')
    db_password = os.getenv('DATABASE_PASSWORD')

    database = Database(
        dbname=db_name,
        host=db_host,
        port=db_port,
        user=db_user,
        db_password=db_password
    )