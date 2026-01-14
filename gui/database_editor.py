import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.db import init_db

class DatabaseEditor:
    def __init__(self, parent, conn):
        self.conn = conn
        self.parent = parent
        self.selected_task_id = None
        
        # 🔥 СТРОКА 1: Сначала создаем окно
        self.window = tk.Toplevel(parent.root)
        self.window.title("🗄️ Редактор базы данных")
        self.window.geometry("900x600")
        
        # 🔥 СТРОКА 2: ПОСЛЕ создания окна настраиваем protocol
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        self.refresh_table()
    
    def setup_ui(self):
        # Кнопки управления (старая строка)
        btn_frame1 = tk.Frame(self.window)
        btn_frame1.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame1, text="🔄 Обновить", command=self.refresh_table, bg="#4CAF50").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame1, text="✏️ Редактировать", command=self.edit_selected, bg="#FF9800").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame1, text="✅ Завершить", command=self.complete_selected, bg="#2196F3").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame1, text="🗑️ Удалить", command=self.delete_selected, bg="#F44336").pack(side=tk.LEFT, padx=5)
        
        # 🔥 НОВЫЕ КНОПКИ АВТОЗАПОЛНЕНИЯ (2 строка)
        btn_frame2 = tk.Frame(self.window)
        btn_frame2.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(btn_frame2, text="😴 Заполнить Сон (00:00-08:00)", command=self.fill_sleep, 
                bg="#795548", fg="white", width=25).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame2, text="☕ Заполнить Отдых (пустые места)", command=self.fill_rest, 
                bg="#607D8B", fg="white", width=25).pack(side=tk.LEFT, padx=5)
        
        # Таблица (остальное без изменений)
        columns = ("ID", "Тег", "Описание", "Старт", "Конец", "Длительность")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings", height=20)
        
        self.sort_column = None
        self.sort_reverse = False
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=130)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        v_scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=v_scrollbar.set)


    def sort_by_column(self, col):
        """Сортировка по клику на заголовок"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_column = col
        
        # Загружаем и сортируем данные
        c = self.conn.cursor()
        c.execute("SELECT id, tag, desc, start, end FROM tasks ORDER BY id DESC")
        data = c.fetchall()
        
        # Функция сортировки
        def sort_key(item):
            id, tag, desc, start, end = item
            if col == "ID": return int(id)
            if col == "Тег": return tag.lower()
            if col == "Описание": return desc.lower()
            if col == "Старт": return start or ""
            if col == "Конец": return end or ""
            if col == "Длительность":
                if end: return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()
                return 0
            return 0
        
        data.sort(key=sort_key, reverse=self.sort_reverse)
        
        # Обновляем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        for task in data:
            id, tag, desc, start, end = task
            duration = "⏳" if not end else f"{self.format_duration(start, end)}"
            self.tree.insert("", "end", values=(id, tag, desc[:30], start[:16] if start else "", end[:16] if end else "", duration))
        
        # Стрелка сортировки
        for c in self.tree["columns"]:
            self.tree.heading(c, text=c)
        arrow = " ▼" if self.sort_reverse else " ▲"
        self.tree.heading(col, text=f"{col}{arrow}")

    
    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        c = self.conn.cursor()
        c.execute("SELECT id, tag, desc, start, end FROM tasks ORDER BY id DESC")
        
        for task in c.fetchall():
            id, tag, desc, start, end = task
            duration = "⏳" if not end else f"{self.format_duration(start, end)}"
            self.tree.insert("", "end", values=(id, tag, desc[:30], start[:16], end[:16] if end else "", duration))
    
    def format_duration(self, start, end):
        try:
            duration = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() / 60
            return f"{duration:.1f}м"
        except:
            return "0м"
    
    def on_select(self, event):
        selection = self.tree.selection()
        self.selected_task_id = None
        if selection:
            item = self.tree.item(selection[0])
            self.selected_task_id = item['values'][0]
    
    def edit_selected(self):
        if not self.selected_task_id:
            messagebox.showwarning("Предупреждение", "Выберите задание!")
            return
        
        # ПРОСТОЕ окно без grid и trace
        edit_window = tk.Toplevel(self.window)
        edit_window.title(f"Редактировать #{self.selected_task_id}")
        edit_window.geometry("400x350")
        
        # Загружаем данные
        c = self.conn.cursor()
        c.execute("SELECT tag, desc, start, end FROM tasks WHERE id = ?", (self.selected_task_id,))
        task = c.fetchone() or ("", "", "", "")
        tag, desc, start_time, end_time = task
        
        # Форма (ПРОСТЫЕ pack)
        tk.Label(edit_window, text="Тег:").pack(pady=5)
        tag_entry = tk.Entry(edit_window, width=30)
        tag_entry.insert(0, tag)
        tag_entry.pack()
        
        tk.Label(edit_window, text="Описание:").pack(pady=5)
        desc_entry = tk.Entry(edit_window, width=30)
        desc_entry.insert(0, desc)
        desc_entry.pack()
        
        tk.Label(edit_window, text="Старт (YYYY-MM-DD HH:MM):").pack(pady=(20,5))
        start_entry = tk.Entry(edit_window, width=30)
        start_entry.insert(0, start_time[:16] if start_time else "")
        start_entry.pack()
        
        tk.Label(edit_window, text="Конец (YYYY-MM-DD HH:MM):").pack(pady=5)
        end_entry = tk.Entry(edit_window, width=30)
        end_entry.insert(0, end_time[:16] if end_time else "")
        end_entry.pack()
        
        # Кнопки
        btn_frame = tk.Frame(edit_window)
        btn_frame.pack(pady=20)
        
        def save_changes():
            try:
                new_tag = tag_entry.get()
                new_desc = desc_entry.get()
                new_start = start_entry.get()
                new_end = end_entry.get()
                
                # Валидация времени
                if new_start:
                    datetime.fromisoformat(new_start.replace(' ', 'T') + ':00')
                if new_end:
                    datetime.fromisoformat(new_end.replace(' ', 'T') + ':00')
                
                # Сохраняем
                c.execute("""
                    UPDATE tasks SET tag=?, desc=?, start=?, end=? WHERE id=?
                """, (new_tag, new_desc, new_start, new_end, self.selected_task_id))
                self.conn.commit()
                self.refresh_table()
                edit_window.destroy()
                messagebox.showinfo("✅ Готово", "Запись обновлена!")
            except:
                messagebox.showerror("Ошибка", "Формат времени: 2026-01-14 14:30")
        
        tk.Button(btn_frame, text="💾 Сохранить", command=save_changes, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="❌ Отмена", command=edit_window.destroy, bg="#F44336", fg="white").pack(side=tk.LEFT, padx=10)


    def complete_selected(self):
        if not self.selected_task_id:
            messagebox.showwarning("Предупреждение", "Выберите задание!")
            return
        
        c = self.conn.cursor()
        c.execute("UPDATE tasks SET end = datetime('now') WHERE id = ?", (self.selected_task_id,))
        self.conn.commit()
        self.refresh_table()
        messagebox.showinfo("Готово", f"Завершено #{self.selected_task_id}")
    
    def delete_selected(self):
        if not self.selected_task_id:
            messagebox.showwarning("Предупреждение", "Выберите задание!")
            return
        
        if messagebox.askyesno("Удалить", f"Удалить #{self.selected_task_id}?"):
            c = self.conn.cursor()
            c.execute("DELETE FROM tasks WHERE id = ?", (self.selected_task_id,))
            self.conn.commit()
            self.refresh_table()
            messagebox.showinfo("Готово", "Удалено!")
    
    def fill_sleep(self):
        """Заполняет Сон 00:00-08:00 для сегодняшнего дня"""
        c = self.conn.cursor()
        today = datetime.now().date().isoformat()
        
        # Удаляем старый сон
        c.execute("DELETE FROM tasks WHERE tag = 'Сон' AND DATE(start) = ?", (today,))
        
        # Добавляем новый сон 00:00-08:00
        c.execute("""
            INSERT INTO tasks (tag, desc, start, end) 
            VALUES ('Сон', 'Авто: утренний сон', ?, ?)
        """, (f"{today}T00:00:00", f"{today}T08:00:00"))
        
        self.conn.commit()
        self.refresh_table()
        messagebox.showinfo("😴 Готово!", "Сон 00:00-08:00 добавлен!")

    def fill_rest(self):
        """Заполняет ВСЕ пустые места Отдыхом (кроме сна)"""
        c = self.conn.cursor()
        today = datetime.now().date().isoformat()
        
        # Удаляем старый отдых
        c.execute("DELETE FROM tasks WHERE tag = 'Отдых' AND DATE(start) = ?", (today,))
        
        # Находим все задания за день (кроме Отдых)
        c.execute("""
            SELECT start, end FROM tasks 
            WHERE DATE(start) = ? AND tag != 'Отдых'
            ORDER BY start
        """, (today,))
        
        tasks = c.fetchall()
        day_start = f"{today}T08:00:00"  # После сна
        day_end = f"{today}T23:59:59"
        
        # Заполняем промежутки
        prev_end = datetime.fromisoformat(day_start)
        
        for start, end in tasks:
            task_start = datetime.fromisoformat(start)
            if (task_start - prev_end).total_seconds() / 60 > 30:  # Промежуток >30мин
                c.execute("""
                    INSERT INTO tasks (tag, desc, start, end) 
                    VALUES ('Отдых', 'Авто: свободное время', ?, ?)
                """, (prev_end.isoformat(), start))
            prev_end = datetime.fromisoformat(end) if end else task_start
        
        # До конца дня
        if (datetime.fromisoformat(day_end) - prev_end).total_seconds() / 60 > 30:
            c.execute("""
                INSERT INTO tasks (tag, desc, start, end) 
                VALUES ('Отдых', 'Авто: свободное время', ?, ?)
            """, (prev_end.isoformat(), day_end))
        
        self.conn.commit()
        self.refresh_table()
        messagebox.showinfo("☕ Готово!", "Все пустые места заполнены Отдыхом!")


    def on_closing(self):
        """Закрытие окна"""
        self.window.destroy()
