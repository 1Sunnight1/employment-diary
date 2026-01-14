import tkinter as tk
from tkinter import ttk, messagebox
from database.db import init_db, add_task

class EmploymentDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Employment Diary")
        self.root.geometry("500x400")
        self.conn = init_db()
        self.active_tasks = []
        self.setup_ui()
    
    def setup_ui(self):
        tk.Label(self.root, text="Тег:").pack(pady=5)
        self.tag_entry = tk.Entry(self.root, width=20)
        self.tag_entry.pack()
        
        tk.Label(self.root, text="Описание:").pack(pady=5)
        self.desc_entry = tk.Entry(self.root, width=30)
        self.desc_entry.pack()
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Старт", command=self.start_task, bg="green", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.root, text="Активные задания:").pack(pady=(20,5))
        self.task_listbox = tk.Listbox(self.root, height=10)
        self.task_listbox.pack(fill=tk.BOTH, expand=True, padx=20)
    
    def start_task(self):
        tag = self.tag_entry.get()
        desc = self.desc_entry.get()
        if not tag:
            messagebox.showerror("Ошибка", "Введите тег!")
            return
        
        task_id = add_task(self.conn, tag, desc)
        self.task_listbox.insert(0, f"{tag} - {desc} [ID: {task_id}]")
        self.tag_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
