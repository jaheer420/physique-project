# backend/db.py

import os
from mysql.connector import pooling

# ----------------------------
# MySQL Settings (Railway ENV)
# ----------------------------
DB_HOST = os.getenv("MYSQLHOST")
DB_PORT = int(os.getenv("MYSQLPORT", "3306"))
DB_USER = os.getenv("MYSQLUSER")
DB_PASSWORD = os.getenv("MYSQLPASSWORD")
DB_NAME = os.getenv("MYSQLDATABASE")

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

            autocommit=True,

            # ✅ REQUIRED for Railway public proxy
            ssl_disabled=False
        )

    return _pool


def get_conn():
    return get_pool().get_connection()
