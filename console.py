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

def main():
    while True:
        print("\n=== Employment Diary ===")
        print("1. Добавить задание")
        print("2. Выход")
        choice = input("Выберите (1-2): ")
        
        if choice == '1':
            tag = input("Тег (учеба/работа/спорт): ")
            desc = input("Описание (Enter для пропуска): ")
            add_task(tag, desc)
        elif choice == '2':
            break

if __name__ == "__main__":
    main()
