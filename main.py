from gui.app import EmploymentDiary
import tkinter as tk
from database.db import init_db
import atexit

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = EmploymentDiary(root)
    
    # 🔥 КРИТИЧНО: закрытие БД при выходе
    def on_closing():
        app.conn.close()  # Закрываем основное соединение
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)  # Перехватываем крестик
    root.mainloop()
