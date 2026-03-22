import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = "localhost"
        self.database = "sistema_cursos"
        self.user = "root"
        self.password = ""
        self.connection = None
        self.cursor = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except Error as e:
            print(f"Erro ao conectar: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
    
    def execute_query(self, query, params=None):
        try:
            self.connect()
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Error as e:
            print(f"Erro na query: {e}")
            return False
        finally:
            self.disconnect()
    
    def fetch_all(self, query, params=None):
        try:
            self.connect()
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro na busca: {e}")
            return []
        finally:
            self.disconnect()
    
    def fetch_one(self, query, params=None):
        try:
            self.connect()
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except Error as e:
            print(f"Erro na busca: {e}")
            return None
        finally:
            self.disconnect()
