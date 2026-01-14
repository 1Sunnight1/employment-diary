import sqlite3
from datetime import datetime
from collections import defaultdict

def init_db():
    conn = sqlite3.connect('employment_diary.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (id INTEGER PRIMARY KEY, tag TEXT, desc TEXT, start TEXT, end TEXT)''')
    conn.commit()
    return conn

def add_task(conn, tag, desc):
    start = datetime.now().isoformat()
    c = conn.cursor()
    c.execute("INSERT INTO tasks (tag, desc, start) VALUES (?, ?, ?)", (tag, desc, start))
    conn.commit()
    return c.lastrowid

def stop_task(conn, task_id):
    end = datetime.now().isoformat()
    c = conn.cursor()
    c.execute("UPDATE tasks SET end = ? WHERE id = ?", (end, task_id))
    conn.commit()

def get_stats(conn):  # ← НОВОЕ
    c = conn.cursor()
    c.execute("""
        SELECT tag, 
               COUNT(*) as count,
               SUM((julianday(end) - julianday(start)) * 24 * 60) as total_minutes
        FROM tasks 
        WHERE end IS NOT NULL 
        GROUP BY tag 
        ORDER BY total_minutes DESC
    """)
    return c.fetchall()
