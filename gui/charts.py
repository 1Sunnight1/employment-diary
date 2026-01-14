import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db import get_daily_stats, get_tag_pie_data, get_daily_tag_stats
from datetime import datetime

class ChartsView:
    def __init__(self, parent, conn):
        self.conn = conn
        self.window = tk.Toplevel(parent.root)
        self.window.title("📈 Графики продуктивности")
        self.window.geometry("1000x700")
        self.setup_notebook()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        plt.close('all')  # Закрываем matplotlib
        self.window.destroy()


    
    def setup_notebook(self):
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка 1: Столбцы по дням и тегам
        daily_frame = ttk.Frame(notebook)
        notebook.add(daily_frame, text="📊 По дням")
        self.plot_daily_chart(daily_frame)
        
        # Вкладка 2: Круговая диаграмма по тегам
        tag_frame = ttk.Frame(notebook)
        notebook.add(tag_frame, text="🥧 По тегам")
        self.plot_tag_pie(tag_frame)
    
    def plot_daily_chart(self, parent):
        fig, ax = plt.subplots(figsize=(12, 6))
        daily_stats = get_daily_tag_stats(self.conn)
        
        if not daily_stats:
            ax.text(0.5, 0.5, 'Нет данных за последние 30 дней', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=14, color='gray')
        else:
            # Группируем данные по дням
            days_data = {}
            for day, tag, minutes in daily_stats:
                if day not in days_data:
                    days_data[day] = {}
                days_data[day][tag] = minutes
            
            # Подготовка данных
            all_days = sorted(days_data.keys())
            all_tags = sorted(set(tag for day_data in days_data.values() for tag in day_data))
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
            
            # Столбцы для каждого дня
            bar_width = 0.8 / len(all_tags)
            x_pos = range(len(all_days))
            
            for i, tag in enumerate(all_tags):
                minutes_per_day = [days_data[day].get(tag, 0) for day in all_days]
                ax.bar([p + i * bar_width for p in x_pos], minutes_per_day, 
                       bar_width, label=tag, color=colors[i % len(colors)], alpha=0.8)
            
            ax.set_title('Продуктивность по дням и тегам', fontsize=16, fontweight='bold')
            ax.set_xlabel('Дни', fontsize=12)
            ax.set_ylabel('Минут', fontsize=12)
            ax.set_xticks([p + bar_width * (len(all_tags) - 1) / 2 for p in x_pos])
            ax.set_xticklabels([day[5:10] for day in all_days], rotation=45, ha='right')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def plot_tag_pie(self, parent):
        fig, ax = plt.subplots(figsize=(8, 8))
        stats = get_tag_pie_data(self.conn)
        
        if not stats:
            ax.text(0.5, 0.5, 'Нет завершенных заданий', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=14, color='gray')
        else:
            labels = [f"{tag}\n{minutes:.0f}м" for tag, minutes in stats]
            sizes = [minutes for _, minutes in stats]
            colors = plt.cm.Set3(range(len(labels)))
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                            colors=colors, startangle=90, textprops={'fontsize': 10})
            ax.set_title('Распределение времени по тегам', fontsize=16, fontweight='bold')
            plt.setp(autotexts, size=10, weight="bold")
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
