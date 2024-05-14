import base64
import re
import json
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkFont, Entry, Button, Checkbutton, Label, IntVar, PhotoImage, Frame
import hashlib
from cryptography.fernet import Fernet
import asyncio
from task_interface import TaskInterface  # Move TaskInterface to a separate module
from profile_interface import ProfileInterface  # Move ProfileInterface to a separate module


class LoginInterface:
    def __init__(self, master, verify_key_callback, on_success):
        self.terms_checkbox = None
        self.agree_var = None
        self.authenticate_button = None
        self.key_entry = None
        self.placeholder_text = None
        self.label = None
        self.logo_image = None
        self.master = master
        self.verify_key_callback = verify_key_callback
        self.on_success = on_success
        self.create_login_interface()

    def create_login_interface(self):
        self.master.geometry('800x450')
        self.master.configure(bg='#23272A')

        standard_font = tkFont.Font(family='Helvetica', size=15)
        header_font = tkFont.Font(family='Helvetica', size=15, weight='bold')

        self.logo_image = PhotoImage(file='botlogo.png')
        logo_label = Label(self.master, image=self.logo_image, bg='#23272A')
        logo_label.pack(pady=(40, 10))

        self.label = Label(self.master, text="Enter Authentication Key", bg='#23272A', fg='white', font=header_font)
        self.label.pack(pady=10)
        self.placeholder_text = 'Enter Key Here'
        self.key_entry = Entry(self.master, justify='center', fg='white', bg='#343746', bd=0, font=standard_font)
        self.key_entry.pack(ipady=5, ipadx=10, pady=10)
        self.key_entry.insert(0, self.placeholder_text)
        self.key_entry.bind("<FocusIn>", self.clear_placeholder)
        self.key_entry.bind("<FocusOut>", self.add_placeholder)
        self.authenticate_button = Button(self.master, text="Authenticate", command=self.authenticate, fg='white',
                                          bg='#4B0082', bd=0, font=standard_font, padx=20, pady=10)
        self.authenticate_button.pack(pady=20)
        self.agree_var = IntVar()
        self.terms_checkbox = Checkbutton(self.master, text="I agree to the Terms and service", variable=self.agree_var,
                                          onvalue=1, offvalue=0, bg='#23272A', fg='white', selectcolor='#23272A',
                                          activebackground='#23272A', font=standard_font)
        self.terms_checkbox.pack(pady=10)

    def clear_placeholder(self, event):
        if self.key_entry.get() == self.placeholder_text:
            self.key_entry.delete(0, tk.END)
            self.key_entry.config(fg='white')

    def add_placeholder(self, event):
        if not self.key_entry.get():
            self.key_entry.config(fg='gray')
            self.key_entry.insert(0, self.placeholder_text)

    def authenticate(self):
        if self.agree_var.get() == 0:
            messagebox.showerror("Terms Agreement", "You must agree to the terms and service to continue.")
            return
        key = self.key_entry.get()
        if self.verify_key_callback(key):
            messagebox.showinfo("Success", "Key is correct. Access granted.")
            self.master.destroy()
            self.on_success()
        else:
            messagebox.showerror("Authentication Failed", "The provided key is incorrect.")


class AutobotApp:
    def __init__(self, root):
        self.logo_image = None
        self.root = root
        self.root.title('AutoBot Main Interface')
        self.root.configure(background='#2C2F33')
        self.root.geometry('800x600')
        self.stored_key_hash = "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
        self.setup_gui()

    def setup_gui(self):
        self.clear_widgets()
        self.logo_image = PhotoImage(file='botlogo.png')
        logo_label = Label(self.root, image=self.logo_image, background='light pink', bd=10)
        logo_label.place(x=20, y=30)
        nav_frame = tk.Frame(self.root, bg='#343746', bd=5)
        nav_frame.place(x=10, y=220, width=200, height=200)
        Button(nav_frame, text="Dashboard", command=self.dashboard).pack(fill='x', pady=5)
        Button(nav_frame, text="Profile", command=self.pprofile).pack(fill='x', pady=5)
        Button(nav_frame, text="Tasks", command=self.task).pack(fill='x', pady=5)
        content_frame = tk.Frame(self.root, bg='#23272A')
        content_frame.place(x=200, y=50, width=580, height=500)
        Label(content_frame, text="Items checked out", bg='#23272A', fg='white').pack(pady=20)
        Label(content_frame, text="Item checked out!", bg='#23272A', fg='white').pack()

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def dashboard(self):
        self.clear_widgets()
        self.setup_gui()
        print("Dashboard menu clicked")

    def pprofile(self):
        self.clear_widgets()
        profile_app = ProfileInterface(self.root, self)
        print("Profile interface opened")

    def task(self):
        print("Task button clicked")
        TaskInterface(self.root, self)

    def verify_key(self, key):
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key_hash == self.stored_key_hash

    def on_login_success(self):
        self.root.deiconify()

    def show_profile(self):
        self.clear_widgets()
        ProfileInterface(self.root, self)
        print("Profile interface opened")

    def dashboard(self):
        self.clear_widgets()
        self.setup_gui()
        print("Dashboard menu clicked")

    def get_profile_names(self):
        try:
            with open('user_profiles.json', 'r') as file:
                profiles = json.load(file)
            profile_names = [profile['Profile Name'] for profile in profiles]
            return profile_names
        except FileNotFoundError:
            print("The profile file does not exist.")
            return []
        except json.JSONDecodeError:
            print("Error decoding JSON.")
            return []


if __name__ == "__main__":
    main_root = tk.Tk()
    main_root.withdraw()
    app = AutobotApp(main_root)
    login_root = tk.Toplevel()
    login_interface = LoginInterface(login_root, app.verify_key, app.on_login_success)
    main_root.mainloop()
