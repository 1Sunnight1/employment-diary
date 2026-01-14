from gui.app import EmploymentDiary
import tkinter as tk
from database.db import init_db

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = EmploymentDiary(root)
    root.mainloop()
