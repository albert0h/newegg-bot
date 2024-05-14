import tkinter as tk
from tkinter import ttk, messagebox
from cryptography.fernet import Fernet
import base64
import json
import asyncio
from newegg_module import AutoBot  # Add this line to import the AutoBot class


class TaskInterface:
    def __init__(self, root, app):
        self.logo_image = None
        self.root = root
        self.app = app
        self.tasks = {}
        self.task_vars = {}
        self.task_list_frame = None
        self.setup_ui()

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#121212')
        style.configure('TButton', font=('Helvetica', 12), background='#333333', foreground='white', relief='flat')
        style.configure('TCheckbutton', font=('Helvetica', 10), background='#121212', foreground='white',
                        selectcolor='#333333', relief='flat')

        btn_frame = ttk.Frame(self.root, style='TFrame')
        btn_frame.pack(side='left', fill='y', padx=2, pady=2)

        self.logo_image = tk.PhotoImage(file='botlogo.png')
        logo_label = tk.Label(self.root, image=self.logo_image, borderwidth=2, relief='solid', bg='#23272A')
        logo_label.pack(side='top', pady=10)

        ttk.Button(btn_frame, text="Dashboard", command=self.app.dashboard).pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Edit Task", command=self.edit_task).pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Delete Task", command=self.delete_task).pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Create Task", command=self.create_task).pack(fill='x', pady=5)

        self.task_list_frame = ttk.Frame(self.root, style='TFrame')
        self.task_list_frame.pack(side='right', fill='both', expand=True, padx=20, pady=20)

        self.load_tasks()

        control_frame = ttk.Frame(self.root, style='TFrame')
        control_frame.place(relx=0.4, rely=0.85, anchor='center')
        ttk.Button(control_frame, text="Start", command=self.start_all_tasks).pack(side='left', padx=10, pady=10)
        ttk.Button(control_frame, text="Stop", command=self.stop_all_tasks).pack(side='left', padx=10, pady=10)

    def load_key(self):
        try:
            with open('secret.key', 'rb') as key_file:
                return key_file.read()
        except FileNotFoundError:
            raise FileNotFoundError("The encryption key file 'secret.key' was not found.")

    def encrypt_password(self, password, key):
        fernet = Fernet(key)
        return fernet.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password, key):
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_password.encode()).decode()

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as file:
                tasks_data = json.load(file)
            if isinstance(tasks_data, list):
                self.tasks = {str(i + 1): task for i, task in enumerate(tasks_data)}
            else:
                self.tasks = tasks_data

            for widget in self.task_list_frame.winfo_children():
                widget.destroy()

            for task_id, task in self.tasks.items():
                var = tk.IntVar()
                task_text = f"{task['Task Name']} - {task['Profile Used']}"
                chk = ttk.Checkbutton(self.task_list_frame, text=task_text, variable=var, style='TCheckbutton')
                chk.pack(anchor='w', pady=10)
                self.task_vars[task_id] = var
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {str(e)}")

    def save_tasks(self):
        with open('tasks.json', 'w') as file:
            json.dump(self.tasks, file, indent=4)

    def create_task(self):
        key = self.load_key()
        fernet = Fernet(key)

        create_window = tk.Toplevel(self.root)
        create_window.title("Create New Task")
        create_window.geometry("300x200")

        tk.Label(create_window, text="Task Name:").pack()
        task_name_entry = tk.Entry(create_window)
        task_name_entry.pack()

        tk.Label(create_window, text="Product Link:").pack()
        product_link_entry = tk.Entry(create_window)
        product_link_entry.pack()

        tk.Label(create_window, text="Select Profile:").pack()
        profiles = self.app.get_profile_names()
        selected_profile = tk.StringVar(create_window)
        selected_profile.set(profiles[0] if profiles else "No profiles available")
        profile_menu = tk.OptionMenu(create_window, selected_profile, *profiles)
        profile_menu.pack()

        tk.Label(create_window, text="Account Password:").pack()
        password_entry = tk.Entry(create_window, show="*")
        password_entry.pack()

        def save_task():
            encrypted_password = fernet.encrypt(password_entry.get().encode()).decode()
            task_id = str(max([int(k) for k in self.tasks.keys()], default=0) + 1)
            self.tasks[task_id] = {
                "Task Name": task_name_entry.get(),
                "Product Link": product_link_entry.get(),
                "Profile Used": selected_profile.get(),
                "Account Password": encrypted_password
            }
            self.save_tasks()
            create_window.destroy()
            self.load_tasks()

        tk.Button(create_window, text="Save Task", command=save_task).pack()

    def edit_task(self):
        key = self.load_key()
        fernet = Fernet(key)
        selected_task_ids = [task_id for task_id, var in self.task_vars.items() if var.get() == 1]
        if not selected_task_ids:
            messagebox.showerror("Error", "Please select a task to edit.")
            return

        task_id = selected_task_ids[0]
        task = self.tasks[task_id]
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("300x200")

        tk.Label(edit_window, text="Task Name:").pack()
        task_name_entry = tk.Entry(edit_window)
        task_name_entry.insert(0, task['Task Name'])
        task_name_entry.pack()

        tk.Label(edit_window, text="Product Link:").pack()
        product_link_entry = tk.Entry(edit_window)
        product_link_entry.insert(0, task['Product Link'])
        product_link_entry.pack()

        tk.Label(edit_window, text="Select Profile:").pack()
        profiles = self.app.get_profile_names()
        selected_profile = tk.StringVar(edit_window)
        selected_profile.set(task['Profile Used'])
        profile_menu = tk.OptionMenu(edit_window, selected_profile, *profiles)
        profile_menu.pack()

        tk.Label(edit_window, text="Account Password:").pack()
        password_entry = tk.Entry(edit_window, show="*")
        try:
            initial_password = fernet.decrypt(task['Account Password'].encode()).decode()
            password_entry.insert(0, initial_password)
        except InvalidToken:
            messagebox.showerror("Error", "Invalid password token.")
            password_entry.insert(0, "")

        password_entry.pack()

        def save_edited_task():
            encrypted_password = fernet.encrypt(password_entry.get().encode()).decode()
            self.tasks[task_id]['Task Name'] = task_name_entry.get()
            self.tasks[task_id]['Product Link'] = product_link_entry.get()
            self.tasks[task_id]['Profile Used'] = selected_profile.get()
            self.tasks[task_id]['Account Password'] = encrypted_password
            self.save_tasks()
            edit_window.destroy()
            self.load_tasks()

        tk.Button(edit_window, text="Save Changes", command=save_edited_task).pack()

    def delete_task(self):
        selected_task_ids = [task_id for task_id, var in self.task_vars.items() if var.get() == 1]
        if not selected_task_ids:
            messagebox.showerror("Error", "Please select a task to delete.")
            return
        for task_id in selected_task_ids:
            del self.tasks[task_id]
        self.save_tasks()
        self.load_tasks()

    def start_all_tasks(self):
        for task_id, var in self.task_vars.items():
            if var.get() == 1:
                task = self.tasks[task_id]
                profile_name = task['Profile Used']
                product_link = task['Product Link']
                password = self.decrypt_password(task['Account Password'], self.load_key())

                with open('user_profiles.json', 'r') as file:
                    profiles = json.load(file)
                profile = next((p for p in profiles if p['Profile Name'] == profile_name), None)

                if profile:
                    asyncio.run(self.start_task(profile, product_link, password))
                else:
                    messagebox.showerror("Error", f"Profile '{profile_name}' not found.")

    async def start_task(self, profile, product_link, password):
        print(f"Starting task with profile: {profile['Profile Name']} and product link: {product_link}")
        bot = AutoBot(profile, product_link, password)
        await bot.start_bot()

    def stop_all_tasks(self):
        print("Stopping all tasks...")
