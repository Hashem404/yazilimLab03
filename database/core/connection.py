"""
PostgreSQL veritabanı bağlantı ayarları
"""

import os
import psycopg2
from psycopg2 import pool
from typing import Optional


class DatabaseConfig:
    def __init__(self):
        self.host = os.environ.get('DB_HOST', 'localhost')
        self.port = os.environ.get('DB_PORT', '5432')
        self.database = os.environ.get('DB_NAME', 'universite_sinav_db')
        self.user = os.environ.get('DB_USER', 'postgres')
        self.password = os.environ.get('DB_PASSWORD', 'postgres')
    
    def get_connection_string(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"
    
    def get_connection_dict(self) -> dict:
        return {
            'host': self.host,
            'port': self.port,
            'dbname': self.database,
            'user': self.user,
            'password': self.password
        }


class DatabaseConnection:
    
    _instance: Optional['DatabaseConnection'] = None
    _pool: Optional[pool.SimpleConnectionPool] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        try:
            config = DatabaseConfig()
            self._pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **config.get_connection_dict()
            )
            print("Veritabanı bağlantı havuzu başarıyla oluşturuldu.")
        except psycopg2.Error as e:
            print(f"Veritabanı bağlantı hatası: {e}")
            raise
    
    def get_connection(self):
        if self._pool is None:
            self._initialize_pool()
        return self._pool.getconn()
    
    def release_connection(self, conn):
        if self._pool is not None:
            self._pool.putconn(conn)
    
    def close_all(self):
        """Tüm bağlantıları kapatır"""
        if self._pool is not None:
            self._pool.closeall()
            self._pool = None
            print("Tüm veritabanı bağlantıları kapatıldı.")


_db_connection: Optional[DatabaseConnection] = None


def get_connection():
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection.get_connection()


def release_connection(conn):
    global _db_connection
    if _db_connection is not None:
        _db_connection.release_connection(conn)


def close_all_connections():
    global _db_connection
    if _db_connection is not None:
        _db_connection.close_all()
        _db_connection = None
