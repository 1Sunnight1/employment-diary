import sqlite3
from datetime import datetime

conn = sqlite3.connect('dayly_checker.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, tag TEXT, desc TEXT, start TEXT, end TEXT)''')

def add_task(tag, desc):
    start = datetime.now().isoformat()
    c.execute("INSERT INTO tasks (tag, desc, start) VALUES (?, ?, ?)", (tag, desc, start))
    conn.commit()
