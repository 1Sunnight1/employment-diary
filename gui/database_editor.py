import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime  
from database.db import init_db

class DatabaseEditor:
    def __init__(self, parent, conn):
        self.conn = conn
        self.parent = parent
        
        # Главное окно редактора
        self.window = tk.Toplevel(parent.root)
        self.window.title("🗄️ Редактор базы данных")
        self.window.geometry("900x600")
        
        self.selected_task_id = None
        self.setup_ui()
        self.refresh_table()
    
    def setup_ui(self):
        # Кнопки управления
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="🔄 Обновить", command=self.refresh_table, bg="#4CAF50").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✏️ Редактировать", command=self.edit_selected, bg="#FF9800").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✅ Завершить", command=self.complete_selected, bg="#2196F3").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Удалить", command=self.delete_selected, bg="#F44336").pack(side=tk.LEFT, padx=5)
        
        # Таблица заданий
        columns = ("ID", "Тег", "Описание", "Старт", "Конец", "Длительность")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
    
    def refresh_table(self):
        # Очищаем таблицу
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
            messagebox.showwarning("Предупреждение", "Выберите задание для редактирования!")
            return
        
        # Окно редактирования
        edit_window = tk.Toplevel(self.window)
        edit_window.title(f"Редактировать задание #{self.selected_task_id}")
        edit_window.geometry("400x300")
        
        c = self.conn.cursor()
        c.execute("SELECT tag, desc, start, end FROM tasks WHERE id = ?", (self.selected_task_id,))
        task = c.fetchone()
        
        tk.Label(edit_window, text="Тег:").pack(pady=5)
        tag_entry = tk.Entry(edit_window, width=30)
        tag_entry.insert(0, task[0] or "")
        tag_entry.pack()
        
        tk.Label(edit_window, text="Описание:").pack(pady=5)
        desc_entry = tk.Entry(edit_window, width=30)
        desc_entry.insert(0, task[1] or "")
        desc_entry.pack()
        
        def save_changes():
            new_tag = tag_entry.get()
            new_desc = desc_entry.get()
            c.execute("UPDATE tasks SET tag = ?, desc = ? WHERE id = ?", 
                     (new_tag, new_desc, self.selected_task_id))
            self.conn.commit()
            self.refresh_table()
            edit_window.destroy()
            messagebox.showinfo("Успех", "Задание обновлено!")
        
        tk.Button(edit_window, text="💾 Сохранить", command=save_changes, bg="#4CAF50").pack(pady=20)
    
    def complete_selected(self):
        if not self.selected_task_id:
            messagebox.showwarning("Предупреждение", "Выберите задание!")
            return
        
        from database.db import stop_task
        stop_task(self.conn, self.selected_task_id)
        self.refresh_table()
        messagebox.showinfo("Успех", f"Задание #{self.selected_task_id} завершено!")
    
    def delete_selected(self):
        if not self.selected_task_id:
            messagebox.showwarning("Предупреждение", "Выберите задание!")
            return
        
        if messagebox.askyesno("Удалить", f"Удалить задание #{self.selected_task_id}?"):
            c = self.conn.cursor()
            c.execute("DELETE FROM tasks WHERE id = ?", (self.selected_task_id,))
            self.conn.commit()
            self.refresh_table()
            messagebox.showinfo("Успех", "Задание удалено!")

    def format_duration(self, start, end):
            try:
                duration = (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() / 60
                return f"{duration:.1f}м"
            except:
                return "0м"