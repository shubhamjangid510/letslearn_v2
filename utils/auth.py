# utils/auth.py
import psycopg2
import hashlib
from utils.database import get_connection

def authenticate_user(email, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, role, class FROM users WHERE email=%s AND password_hash=%s",
                (email, hashlib.sha256(password.encode()).hexdigest()))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return dict(zip(['id', 'name', 'email', 'role', 'class'], row))
    return None