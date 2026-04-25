import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Имя файла для сохранения данных
DATA_FILE = 'expenses.json'

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("700x500")

        self.expenses = self.load_data()

        self.setup_ui()
        self.update_table(self.expenses)

    def setup_ui(self):
        # --- Фрейм добавления расхода ---
        add_frame = tk.LabelFrame(self.root, text="Добавить расход", padx=10, pady=10)
        add_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(add_frame, text="Сумма:").grid(row=0, column=0, padx=5)
        self.amount_entry = tk.Entry(add_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5)

        tk.Label(add_frame, text="Категория:").grid(row=0, column=2, padx=5)
        self.category_cb = ttk.Combobox(add_frame, values=["Еда", "Транспорт", "Развлечения", "ЖКХ", "Другое"], width=15)
        self.category_cb.grid(row=0, column=3, padx=5)

        tk.Label(add_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5)
        self.date_entry = tk.Entry(add_frame, width=12)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Дата по умолчанию - сегодня
        self.date_entry.grid(row=0, column=5, padx=5)

        tk.Button(add_frame, text="Добавить", command=self.add_expense).grid(row=0, column=6, padx=10)

        # --- Фрейм фильтрации ---
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация и Подсчет", padx=10, pady=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5)
        self.filter_category_cb = ttk.Combobox(filter_frame, values=["Все", "Еда", "Транспорт", "Развлечения", "ЖКХ", "Другое"])
        self.filter_category_cb.current(0)
        self.filter_category_cb.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="С:").grid(row=0, column=2, padx=5)
        self.filter_start_date = tk.Entry(filter_frame, width=12)
        self.filter_start_date.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="По:").grid(row=0, column=4, padx=5)
        self.filter_end_date = tk.Entry(filter_frame, width=12)
        self.filter_end_date.grid(row=0, column=5, padx=5)

        tk.Button(filter_frame, text="Применить", command=self.apply_filter).grid(row=0, column=6, padx=5)
        tk.Button(filter_frame, text="Сбросить", command=self.reset_filter).grid(row=0, column=7, padx=5)

        # --- Таблица расходов ---
        self.tree = ttk.Treeview(self.root, columns=("Date", "Category", "Amount"), show="headings", height=12)
        self.tree.heading("Date", text="Дата")
        self.tree.heading("Category", text="Категория")
        self.tree.heading("Amount", text="Сумма")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- Итог ---
        self.total_label = tk.Label(self.root, text="Общая сумма: 0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(anchor=tk.E, padx=20, pady=10)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def validate_inputs(self, amount_str, date_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом.")
                return None, None
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом.")
            return None, None

        try:
            valid_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД.")
            return None, None

        return amount, valid_date

    def add_expense(self):
        amount_str = self.amount_entry.get()
        category = self.category_cb.get()
        date_str = self.date_entry.get()

        if not category:
            messagebox.showerror("Ошибка", "Выберите или введите категорию.")
            return

        amount, valid_date = self.validate_inputs(amount_str, date_str)
        if amount is None:
            return

        expense = {"date": valid_date, "category": category, "amount": amount}
        self.expenses.append(expense)
        self.save_data()
        
        # Очистка полей
        self.amount_entry.delete(0, tk.END)
        self.update_table(self.expenses)
        messagebox.showinfo("Успех", "Расход успешно добавлен!")

    def update_table(self, data):
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        total = 0
        # Заполняем отсортированными по дате
        for exp in sorted(data, key=lambda x: x['date'], reverse=True):
            self.tree.insert("", tk.END, values=(exp['date'], exp['category'], f"{exp['amount']:.2f}"))
            total += exp['amount']
        
        self.total_label.config(text=f"Сумма за период: {total:.2f}")

    def apply_filter(self):
        cat = self.filter_category_cb.get()
        start_date = self.filter_start_date.get()
        end_date = self.filter_end_date.get()

        filtered_data = self.expenses

        # Фильтр по категории
        if cat and cat != "Все":
            filtered_data = [e for e in filtered_data if e['category'] == cat]

        # Фильтр по начальной дате
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                filtered_data = [e for e in filtered_data if e['date'] >= start_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Начальная дата должна быть в формате ГГГГ-ММ-ДД.")
                return

        # Фильтр по конечной дате
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
                filtered_data = [e for e in filtered_data if e['date'] <= end_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Конечная дата должна быть в формате ГГГГ-ММ-ДД.")
                return

        self.update_table(filtered_data)

    def reset_filter(self):
        self.filter_category_cb.current(0)
        self.filter_start_date.delete(0, tk.END)
        self.filter_end_date.delete(0, tk.END)
        self.update_table(self.expenses)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()