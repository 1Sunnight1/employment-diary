import sqlite3
from datetime import datetime, timedelta 
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

def get_stats(conn):
    c = conn.cursor()
    c.execute("""
        SELECT tag, 
               COUNT(*) as count,
               COUNT(end) as completed_count,
               SUM(CASE WHEN end IS NOT NULL 
                       THEN (strftime('%s', end) - strftime('%s', start)) / 60.0 
                       ELSE 0 END) as total_minutes
        FROM tasks 
        WHERE end IS NOT NULL 
        GROUP BY tag 
        ORDER BY total_minutes DESC
    """)
    return c.fetchall()

def get_daily_stats(conn):
    """Статистика по дням (последние 30 дней)"""
    c = conn.cursor()
    c.execute("""
        SELECT DATE(start) as day,
               COUNT(*) as tasks,
               SUM((strftime('%s', end) - strftime('%s', start)) / 60.0) as total_minutes
        FROM tasks 
        WHERE end IS NOT NULL AND start > date('now', '-30 days')
        GROUP BY DATE(start)
        ORDER BY day
    """)  
    return c.fetchall()


def get_tag_pie_data(conn):
    """Данные для круговой диаграммы по тегам"""
    c = conn.cursor()
    c.execute("""
        SELECT tag, SUM((strftime('%s', end) - strftime('%s', start)) / 60.0) as minutes
        FROM tasks WHERE end IS NOT NULL
        GROUP BY tag
        ORDER BY minutes DESC
        LIMIT 8
    """)
    return c.fetchall()

def get_daily_tag_stats(conn, date_str):
    """Статистика по тегам за день для графиков"""
    c = conn.cursor()
    c.execute("""
        SELECT tag, SUM(
            CASE 
                WHEN end IS NOT NULL 
                THEN (julianday(end) - julianday(start)) * 24 * 60
                ELSE 0 
            END
        ) as minutes
        FROM tasks 
        WHERE DATE(start) = ? AND end IS NOT NULL
        GROUP BY tag
        HAVING minutes > 0
    """, (date_str,))
    return c.fetchall()

