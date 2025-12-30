# backend/db.py

import mysql.connector
from mysql.connector import pooling

# ----------------------------
# MySQL Settings for XAMPP
# ----------------------------
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = ""        # XAMPP default: empty password
DB_NAME = "physique_db" # MUST match your phpMyAdmin database name

# ----------------------------
# Connection Pool
# ----------------------------
_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="physique_pool",
            pool_size=5,
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            autocommit=True
        )
    return _pool

def get_conn():
    return get_pool().get_connection()
