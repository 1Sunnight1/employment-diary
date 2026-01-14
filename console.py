import sqlite3
from datetime import datetime

conn = sqlite3.connect('employment_diary.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks 
             (id INTEGER PRIMARY KEY, tag TEXT, desc TEXT, start TEXT, end TEXT)''')
conn.commit()

def add_task(tag, desc):
    start = datetime.now().isoformat()
    c.execute("INSERT INTO tasks (tag, desc, start) VALUES (?, ?, ?)", (tag, desc, start))
    conn.commit()
    print(f"✅ Задание '{tag}' начато: {start[:16]}")

def show_all_tasks():  # ← НОВОЕ
    c.execute("SELECT id, tag, desc, start, end FROM tasks WHERE end IS NOT NULL")
    completed = c.fetchall()
    if not completed:
        print("❌ Нет завершенных заданий")
        return
    
    print("\n📋 Завершенные задания:")
    print("-" * 60)
    for task in completed:
        id, tag, desc, start, end = task
        duration = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() / 60
        print(f"ID:{id:2} | {tag:8} | {desc[:20]:20} | {duration:5.1f} мин")
    print("-" * 60)

def show_all_tasks_full():  # ← НОВОЕ
    c.execute("SELECT id, tag, start, end FROM tasks ORDER BY id DESC LIMIT 10")
    all_tasks = c.fetchall()
    print("\n🔍 Последние 10 заданий (включая незавершенные):")
    print("-" * 80)
    for task in all_tasks:
        id, tag, start, end = task
        status = "✅" if end else "⏳"
        print(f"ID:{id:2} | {tag:10} | {start[:16]} | {end[:16] if end else 'НЕ ОСТАНОВЛЕНО'} {status}")
    print("-" * 80)

def main():
    while True:
        print("\n=== Employment Diary ===")
        print("1. Добавить задание")
        print("2. Завершенные задания") 
        print("3. ВСЕ задания")
        print("4. Выход")
        choice = input("Выберите (1-4): ")
        
        if choice == '1':
            tag = input("Тег (учеба/работа/спорт): ")
            desc = input("Описание (Enter для пропуска): ")
            add_task(tag, desc)
        elif choice == '2':
            show_all_tasks()
        elif choice == '3':
            show_all_tasks_full()            
        elif choice == '4':
            break

if __name__ == "__main__":
    main()
