import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os
import subprocess

# --- Функции для работы с данными ---

def load_data(filepath="weather_data.json"):
    """Загружает данные о погоде из JSON файла."""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data, filepath="weather_data.json"):
    """Сохраняет данные о погоде в JSON файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def format_for_display(data):
    """Форматирует данные для отображения в таблице."""
    return [
        (entry['date'], entry['temperature'], entry['description'], "Да" if entry['precipitation'] else "Нет")
        for entry in data
    ]

# --- Основное приложение ---

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("800x600")

        self.data = load_data()

        # --- Создание виджетов ---
        self.create_widgets()
        self.update_table()

    def create_widgets(self):
        # --- Фрейм для ввода данных ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить запись", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Поля ввода
        self.date_label = ttk.Label(input_frame, text="Дата (YYYY-MM-DD):")
        self.date_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Автозаполнение текущей датой

        self.temp_label = ttk.Label(input_frame, text="Температура (°C):")
        self.temp_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.temp_entry = ttk.Entry(input_frame)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.desc_label = ttk.Label(input_frame, text="Описание:")
        self.desc_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.desc_entry = ttk.Entry(input_frame)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.precip_label = ttk.Label(input_frame, text="Осадки:")
        self.precip_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.precip_var = tk.StringVar(value="Нет")
        self.precip_combobox = ttk.Combobox(input_frame, textvariable=self.precip_var, values=["Нет", "Да"], state="readonly")
        self.precip_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="Добавить запись", command=self.add_entry)
        self.add_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

        # --- Фрейм для фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтр", padding="10")
        filter_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.filter_date_label = ttk.Label(filter_frame, text="По дате (YYYY-MM-DD):")
        self.filter_date_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.filter_date_entry = ttk.Entry(filter_frame)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.filter_temp_label = ttk.Label(filter_frame, text="Температура > (цифра):")
        self.filter_temp_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.filter_temp_entry = ttk.Entry(filter_frame)
        self.filter_temp_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.apply_filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.apply_filter_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        self.clear_filter_button = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filter)
        self.clear_filter_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # --- Фрейм для таблицы ---
        table_frame = ttk.Frame(self.root, padding="10")
        table_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(table_frame, columns=("Date", "Temperature", "Description", "Precipitation"), show="headings")
        self.tree.heading("Date", text="Дата")
        self.tree.heading("Temperature", text="Температура (°C)")
        self.tree.heading("Description", text="Описание")
        self.tree.heading("Precipitation", text="Осадки")

        # Настройка ширины столбцов
        self.tree.column("Date", width=120, anchor="center")
        self.tree.column("Temperature", width=100, anchor="center")
        self.tree.column("Description", width=250, anchor="w")
        self.tree.column("Precipitation", width=100, anchor="center")

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=scrollbar_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # --- Кнопки сохранения/загрузки ---
        file_frame = ttk.Frame(self.root, padding="10")
        file_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.save_button = ttk.Button(file_frame, text="Сохранить JSON", command=self.save_to_json)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.load_button = ttk.Button(file_frame, text="Загрузить JSON", command=self.load_from_json)
        self.load_button.pack(side=tk.LEFT, padx=5)

    def update_table(self, data_to_display=None):
        """Обновляет содержимое таблицы."""
        if data_to_display is None:
            data_to_display = self.data

        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполняем таблицу отформатированными данными
        for row in format_for_display(data_to_display):
            self.tree.insert("", "end", values=row)

    def validate_entry(self, date_str, temp_str, desc_str):
        """Проверяет корректность ввода."""
        errors = []
        # Проверка даты
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append("Дата должна быть в формате YYYY-MM-DD.")

        # Проверка температуры
        try:
            float(temp_str)
        except ValueError:
            errors.append("Температура должна быть числом.")

        # Проверка описания
        if not desc_str.strip():
            errors.append("Описание погоды не может быть пустым.")

        return errors

    def add_entry(self):
        """Добавляет новую запись о погоде."""
        date_str = self.date_entry.get()
        temp_str = self.temp_entry.get()
        desc_str = self.desc_entry.get()
        precip_str = self.precip_var.get()

        errors = self.validate_entry(date_str, temp_str, desc_str)
        if errors:
            messagebox.showerror("Ошибка ввода", "\n".join(errors))
            return

        temperature = float(temp_str)
        precipitation = True if precip_str == "Да" else False

        new_entry = {
            "date": date_str,
            "temperature": temperature,
            "description": desc_str,
            "precipitation": precipitation
        }

        self.data.append(new_entry)
        save_data(self.data) # Автосохранение при добавлении
        self.update_table()

        # Очистка полей ввода
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set("Нет") # Сброс к значению по умолчанию

    def apply_filter(self):
        """Применяет фильтры к данным."""
        filter_date_str = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        filtered_data = self.data

        # Фильтр по дате
        if filter_date_str:
            try:
                datetime.strptime(filter_date_str, "%Y-%m-%d")
                filtered_data = [entry for entry in filtered_data if entry['date'] == filter_date_str]
            except ValueError:
                messagebox.showerror("Ошибка фильтра", "Дата для фильтрации должна быть в формате YYYY-MM-DD.")
                return

        # Фильтр по температуре
        if filter_temp_str:
            try:
                filter_temp = float(filter_temp_str)
                filtered_data = [entry for entry in filtered_data if entry['temperature'] > filter_temp]
            except ValueError:
                messagebox.showerror("Ошибка фильтра", "Температура для фильтрации должна быть числом.")
                return

        self.update_table(filtered_data)

    def clear_filter(self):
        """Сбрасывает фильтры и обновляет таблицу."""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()

    def save_to_json(self):
        """Сохраняет данные в JSON файл."""
        save_data(self.data)
        messagebox.showinfo("Сохранение", "Данные успешно сохранены в weather_data.json")

    def load_from_json(self):
        """Загружает данные из JSON файла."""
        loaded_data = load_data()
        if loaded_data is not None:
            self.data = loaded_data
            self.update_table()
            messagebox.showinfo("Загрузка", "Данные успешно загружены из weather_data.json")
        else:
            messagebox.showerror("Загрузка", "Ошибка при загрузке данных. Файл может быть поврежден или пуст.")

# --- Функции для работы с Git ---

def initialize_git_repo(project_path):
    """Инициализирует Git репозиторий."""
    if not os.path.exists(os.path.join(project_path, ".git")):
        subprocess.run(["git", "init"], cwd=project_path)
        print("Git репозиторий инициализирован.")
    else:
        print("Git репозиторий уже существует.")

def add_gitignore(project_path):
    """Создает файл .gitignore."""
    gitignore_content = [
        "# Python cache",
        "__pycache__/",
        "*.pyc",
        "",
        "# VS Code settings",
        ".vscode/",
        "",
        "# IDE specific",
        ".idea/",
        "*.iml",
        "",
        "# OS generated files",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# Data files",
        "weather_data.json"
    ]
    gitignore_path = os.path.join(project_path, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("\n".join(gitignore_content))
        print(f"Создан файл .gitignore.")
    else:
        print("Файл .gitignore уже существует.")

def create_readme(project_path, author_name):
    """Создает файл README.md."""
    readme_content = f"""
# Weather Diary

## Автор
{author_name}

