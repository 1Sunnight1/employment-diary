import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db import get_daily_stats, get_tag_pie_data
from datetime import datetime, timedelta

class ChartsView:
    def __init__(self, parent, conn):
        self.conn = conn
        self.parent = parent
        
        # 🔥 ФИКС 1: Сначала создаем окно
        self.window = tk.Toplevel(parent.root)
        self.window.title("📈 Графики продуктивности")
        self.window.geometry("1000x700")
        
        # 🔥 ФИКС 2: ПОТОМ настраиваем закрытие
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_notebook()
    
    def on_closing(self):
        plt.close('all')
        self.window.destroy()
    
    def setup_notebook(self):
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка 1: Столбцы по дням
        daily_frame = ttk.Frame(notebook)
        notebook.add(daily_frame, text="📊 По дням")
        self.plot_daily_chart(daily_frame)
        
        # Вкладка 2: Круговая диаграмма
        tag_frame = ttk.Frame(notebook)
        notebook.add(tag_frame, text="🥧 По тегам")
        self.plot_tag_pie(tag_frame)
    
    def plot_daily_chart(self, parent):
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # 🔥 НОВЫЕ ДАННЫЕ: день + тег + минуты
        c = self.conn.cursor()
        c.execute("""
            SELECT DATE(start) as day, tag, 
                SUM((strftime('%s', end) - strftime('%s', start)) / 60.0) as minutes
            FROM tasks 
            WHERE end IS NOT NULL AND start > date('now', '-14 days')
            GROUP BY DATE(start), tag
            ORDER BY day DESC, minutes DESC
        """)
        raw_data = c.fetchall()
        
        if not raw_data:
            ax.text(0.5, 0.5, 'Нет данных за последние 14 дней\nДобавьте задания!', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=14, color='gray')
        else:
            # Группируем по дням
            days_data = {}
            for day, tag, minutes in raw_data:
                if day not in days_data:
                    days_data[day] = {}
                days_data[day][tag] = minutes
            
            # Подготовка для стекирования
            all_days = sorted(days_data.keys(), reverse=True)  # Новые дни слева
            all_tags = sorted(set(tag for day_data in days_data.values() for tag in day_data))
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                    '#DDA0DD', '#98D8C8', '#F7DC6F', '#A8E6CF', '#FFD93D']
            
            bottom = [0] * len(all_days)
            
            # 🔥 СТЕКИРУЕМ столбцы по тегам
            for i, tag in enumerate(all_tags):
                color = colors[i % len(colors)]
                heights = [days_data[day].get(tag, 0) for day in all_days]
                
                ax.bar(all_days, heights, bottom=bottom, label=tag, 
                    color=color, alpha=0.85, edgecolor='white', linewidth=1)
                bottom = [b + h for b, h in zip(bottom, heights)]
            
            # Настройки графика
            ax.set_title('Продуктивность по дням и тегам (стекированные)', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Дни', fontsize=12)
            ax.set_ylabel('Общее время (минуты)', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            
            # Подписи ИТОГОВЫХ высот
            for i, day in enumerate(all_days):
                total_height = sum(days_data[day].values())
                ax.text(i, total_height + 10, f'{int(total_height)}м', 
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def plot_tag_pie(self, parent):
        fig, ax = plt.subplots(figsize=(10, 8))
        stats = get_tag_pie_data(self.conn)
        
        if not stats:
            ax.text(0.5, 0.5, 'Нет завершенных заданий!\nСтартуйте → Стоп', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=14, color='gray')
        else:
            tags = [row[0] for row in stats]
            minutes = [row[1] for row in stats]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
            
            wedges, texts, autotexts = ax.pie(minutes, labels=tags, autopct='%1.1f%%', 
                                            colors=colors, startangle=90)
            ax.set_title('Распределение времени по тегам', fontsize=16, fontweight='bold')
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
