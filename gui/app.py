import tkinter as tk
from tkinter import ttk, messagebox
from database.db import init_db, add_task

class EmploymentDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Employment Diary")
        self.root.geometry("500x500")
        self.conn = init_db()
        self.active_tasks = {}  # {task_id: "tag - desc"}
        self.setup_ui()
    
    def setup_ui(self):
        # Поля ввода
        tk.Label(self.root, text="Тег:").pack(pady=5)
        self.tag_entry = tk.Entry(self.root, width=20)
        self.tag_entry.pack()
        
        tk.Label(self.root, text="Описание:").pack(pady=5)
        self.desc_entry = tk.Entry(self.root, width=30)
        self.desc_entry.pack()
        
        # Кнопки
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Старт", command=self.start_task, bg="green", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Стоп", command=self.stop_task, bg="red", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Статистика", command=self.show_stats, bg="blue", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Список заданий
        tk.Label(self.root, text="Активные задания:").pack(pady=(20,5))
        self.task_listbox = tk.Listbox(self.root, height=12)
        self.task_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,10))
        
        # Выделение для Стоп
        self.task_listbox.bind('<<ListboxSelect>>', self.on_task_select)
    
    def start_task(self):
        tag = self.tag_entry.get()
        desc = self.desc_entry.get()
        if not tag:
            messagebox.showerror("Ошибка", "Введите тег!")
            return
        
        task_id = add_task(self.conn, tag, desc)
        display_text = f"{tag} - {desc} [ID: {task_id}]"
        self.active_tasks[task_id] = display_text
        self.task_listbox.insert(0, display_text)
        
        self.tag_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", f"Задание #{task_id} начато!")
    
    def on_task_select(self, event):
        selection = self.task_listbox.curselection()
        if selection:
            self.selected_task_id = list(self.active_tasks.keys())[selection[0]]
    
    def stop_task(self):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showerror("Ошибка", "Выберите задание из списка!")
            return
        
        task_id = list(self.active_tasks.keys())[selection[0]]
        # TODO: добавить функцию stop_task в db.py
        del self.active_tasks[task_id]
        self.task_listbox.delete(selection[0])
        messagebox.showinfo("Успех", f"Задание #{task_id} остановлено!")
    
    def show_stats(self):
        # TODO: окно статистики
        messagebox.showinfo("Статистика", "Скоро будет готово!")
