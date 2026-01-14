#!/usr/bin/env python3
import sqlite3
from datetime import datetime
from database.db import init_db, add_task, stop_task, get_stats
import os

def print_banner():
    print("\n" + "="*60)
    print("🚀 EMPLOYMENT DIARY — КОНСОЛЬНАЯ ВЕРСИЯ")
    print("="*60)

def print_menu():
    print("\n📋 МЕНЮ:")
    print("1. ➕ Добавить задачу")
    print("2. ⏹️  Завершить текущую задачу") 
    print("3. 📊 Показать статистику")
    print("4. 🗄️  База данных (все записи)")
    print("5. 😴 Заполнить Сон (00:00-08:00)")
    print("6. ☕ Заполнить Отдых (пустые места)")
    print("7. ✏️  Редактировать запись")
    print("8. 🗑️  Удалить запись")
    print("0. ❌ Выйти")
    print("-"*60)

def show_stats(conn):
    """Статистика как в GUI"""
    print("\n📈 СТАТИСТИКА ПО ТЕГАМ")
    print("-"*40)
    stats = get_stats(conn)
    if not stats:
        print("Нет завершенных заданий!")
        return
    
    total_time = 0
    for tag, count, completed, minutes in stats:
        print(f"📌 {tag:10} | {count:2} заданий | {minutes:.0f}м")
        total_time += minutes
    print(f"\n⏱️  ИТОГО: {total_time:.0f} минут")

def show_all_tasks(conn):
    """Полная база как в GUI"""
    print("\n🗄️  ВСЕ ЗАДАНИЯ (сортировка по ID)")
    print("-"*80)
    print(f"{'ID':<4} {'ТЕГ':<12} {'ОПИСАНИЕ':<25} {'СТАРТ':<19} {'КОНЕЦ':<19} {'ДЛIT.'}")
    print("-"*80)
    
    c = conn.cursor()
    c.execute("SELECT id, tag, desc, start, end FROM tasks ORDER BY id DESC")
    
    for task in c.fetchall():
        id, tag, desc, start, end = task
        duration = "⏳" if not end else f"{format_duration(start, end)}"
        print(f"{id:<4} {tag:<12} {desc[:24]:<25} {start[:16]:<19} {end[:16] if end else '':<19} {duration}")
    
    print("-"*80)

def format_duration(start, end):
    """Форматирует длительность"""
    try:
        duration = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() / 60
        return f"{duration:.0f}м"
    except:
        return "0м"

def fill_sleep(conn):
    """Сон 00:00-08:00"""
    c = conn.cursor()
    today = datetime.now().date().isoformat()
    
    c.execute("DELETE FROM tasks WHERE tag = 'Сон' AND DATE(start) = ?", (today,))
    c.execute("INSERT INTO tasks (tag, desc, start, end) VALUES (?, ?, ?, ?)",
             ('Сон', 'Авто: утренний сон', f"{today}T00:00:00", f"{today}T08:00:00"))
    conn.commit()
    print("✅ Сон 00:00-08:00 добавлен!")

def fill_rest(conn):
    """Заполнить отдых"""
    c = conn.cursor()
    today = datetime.now().date().isoformat()
    
    c.execute("DELETE FROM tasks WHERE tag = 'Отдых' AND DATE(start) = ?", (today,))
    c.execute("""
        SELECT start, end FROM tasks 
        WHERE DATE(start) = ? AND tag != 'Отдых' ORDER BY start
    """, (today,))
    
    tasks = c.fetchall()
    day_start = f"{today}T08:00:00"
    
    prev_end = datetime.fromisoformat(day_start)
    for start, end in tasks:
        if (datetime.fromisoformat(start) - prev_end).total_seconds() / 60 > 30:
            c.execute("INSERT INTO tasks (tag, desc, start, end) VALUES (?, ?, ?, ?)",
                     ('Отдых', 'Авто', prev_end.isoformat(), start))
        prev_end = datetime.fromisoformat(end) if end else datetime.fromisoformat(start)
    
    conn.commit()
    print("✅ Пустые места заполнены отдыхом!")

def edit_task(conn):
    """Редактирование записи"""
    show_all_tasks(conn)
    try:
        task_id = int(input("\nID записи для редактирования: "))
        c = conn.cursor()
        c.execute("SELECT tag, desc, start, end FROM tasks WHERE id = ?", (task_id,))
        task = c.fetchone()
        
        if not task:
            print("❌ Запись не найдена!")
            return
        
        print(f"Текущие данные: {task}")
        new_tag = input(f"Тег [{task[0]}]: ") or task[0]
        new_desc = input(f"Описание [{task[1]}]: ") or task[1]
        new_start = input(f"Старт [{task[2][:16]}]: ") or task[2][:16]
        new_end = input(f"Конец [{task[3][:16] if task[3] else ''}]: ") or task[3]
        
        c.execute("UPDATE tasks SET tag=?, desc=?, start=?, end=? WHERE id=?", 
                 (new_tag, new_desc, new_start, new_end, task_id))
        conn.commit()
        print("✅ Запись обновлена!")
    except:
        print("❌ Ошибка редактирования!")

def delete_task(conn):
    """Удаление записи"""
    show_all_tasks(conn)
    try:
        task_id = int(input("\nID для удаления: "))
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        print("✅ Запись удалена!")
    except:
        print("❌ Ошибка удаления!")

def main():
    conn = init_db()
    
    while True:
        print_banner()
        print_menu()
        
        try:
            choice = input("Выбор (0-8): ").strip()
            
            if choice == '1':
                tag = input("Тег (учеба/работа): ").strip()
                desc = input("Описание: ").strip()
                task_id = add_task(conn, tag, desc)
                print(f"✅ Задача #{task_id} запущена!")
                
            elif choice == '2':
                stop_task(conn, None)  # Завершает последнюю
                print("✅ Задача завершена!")
                
            elif choice == '3':
                show_stats(conn)
                
            elif choice == '4':
                show_all_tasks(conn)
                
            elif choice == '5':
                fill_sleep(conn)
                
            elif choice == '6':
                fill_rest(conn)
                
            elif choice == '7':
                edit_task(conn)
                
            elif choice == '8':
                delete_task(conn)
                
            elif choice == '0':
                break
                
            else:
                print("❌ Неверный выбор!")
                
            input("\nНажмите Enter...")
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    conn.close()

if __name__ == "__main__":
    main()
