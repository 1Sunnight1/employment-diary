import sqlite3
from datetime import datetime

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

def stop_task(conn, task_id):  # ← НОВОЕ
    end = datetime.now().isoformat()
    c = conn.cursor()
    c.execute("UPDATE tasks SET end = ? WHERE id = ?", (end, task_id))
    conn.commit()
