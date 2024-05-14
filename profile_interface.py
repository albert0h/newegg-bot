import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from cryptography.fernet import Fernet
import base64
import json
import re  # Add this line to import the re module


class ProfileInterface:
    def __init__(self, root, app):
        self.logo_image = None
        self.content_frame = None
        self.profile_window = None
        self.root = root
        self.app = app
        self.enable_validation = True
        self.root.title('Profile Management Interface')
        self.root.configure(background='#23272A')
        self.root.geometry('800x600')
        self.entries = {}
        self.profile_vars = {}
        self.key = self.load_key()  # Load the encryption key
        self.cipher = Fernet(self.key)  # Initialize the cipher
        self.setup_profile_gui()

    def load_key(self):
        key_path = 'secret.key'
        try:
            with open(key_path, 'rb') as key_file:
                key = key_file.read()
                print(f"Key loaded successfully: {key}")
        except FileNotFoundError:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as key_file:
                key_file.write(key)
        return key

    def setup_profile_gui(self):
        nav_frame = tk.Frame(self.root, bg='#343746', bd=5)
        nav_frame.place(x=0, y=0, width=200, height=600)
        tk.Button(nav_frame, text="Back to Dashboard", command=self.app.dashboard).pack(fill='x', pady=5)
        tk.Button(nav_frame, text="Create a Profile", command=self.create_profile).pack(fill='x', pady=5)
        tk.Button(nav_frame, text="Edit Profile", command=self.edit_selected_profile).pack(fill='x', pady=5)
        self.add_dashboard_logo()
        self.content_frame = tk.Frame(self.root, bg='#23272A')
        self.content_frame.place(x=200, y=0, width=600, height=600)
        self.load_profiles()
        self.add_dashboard_logo()

    def load_profiles(self):
        delete_button = tk.Button(self.content_frame, text="Delete Selected", command=self.delete_selected_profiles,
                                  bg='#4B0082', fg='white')
        delete_button.pack(pady=20)
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        profiles_label = tk.Label(self.content_frame, text="Profiles:", bg='#23272A', fg='white',
                                  font=('Arial', 12, 'bold'))
        profiles_label.pack(anchor='w', padx=20, pady=10)
        profiles = []
        try:
            with open('user_profiles.json', 'r') as file:
                profiles = json.load(file)
            for profile in profiles:
                var = tk.IntVar()
                cb = tk.Checkbutton(self.content_frame, text=profile['Profile Name'], variable=var, bg='#23272A',
                                    fg='white')
                cb.pack(anchor='w', padx=40, pady=5)
                self.profile_vars[profile['Profile Name']] = var
        except Exception as e:
            messagebox.showerror("Error", "Failed to load profiles: " + str(e))
        delete_button = tk.Button(self.content_frame, text="Delete Selected", command=self.delete_selected_profiles,
                                  bg='#4B0082', fg='white')
        delete_button.pack(pady=20)
        print(self.add_dashboard_logo())

    def add_dashboard_logo(self):
        try:
            self.logo_image = tk.PhotoImage(file='botlogo.png')
            logo_label = tk.Label(self.root, image=self.logo_image, bg='grey', bd=4, relief='solid')
            logo_label.place(relx=0.0225, rely=0.75)
            logo_label.bind('<Button-1>', self.goto_dashboard)
        except Exception as e:
            print("Failed to load or display the logo image:", e)

    def goto_dashboard(self, event=None):
        print("Dashboard menu clicked")
        self.app.dashboard()

    def create_profile(self):
        self.profile_window = tk.Toplevel(self.root)
        self.profile_window.title("Add Profile")
        self.profile_window.geometry("530x620")
        self.profile_window.configure(background='#23272A')
        frame = tk.Frame(self.profile_window, bg='#23272A')
        frame.pack(padx=10, pady=10, fill='both', expand=True)
        fields = ["Profile Name", "First Name", "Last Name", "Email", "Address Line", "City", "State", "Postal Code",
                  "Phone Number", "Card Number", "Expiration Date", "CVV"]
        for i, field in enumerate(fields):
            tk.Label(frame, text=field, bg='#23272A', fg='white').grid(row=i, column=0, padx=10, pady=10, sticky='w')
            entry = tk.Entry(frame, width=45)
            entry.grid(row=i, column=1, padx=10, pady=10)
            self.entries[field] = entry
        tk.Button(frame, text="Save", command=self.save_profile, bg='#4B0082', fg='white').grid(row=len(fields),
                                                                                                column=1,
                                                                                                padx=10, pady=20,
                                                                                                sticky='e')

    def validate_fields(self):
        if not self.enable_validation:
            return True
        error_messages = []
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        phone_regex = r"^\+?1?\d{9,15}$"
        for field, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                error_messages.append(f"{field} cannot be empty.")
            elif field == "Email" and not re.match(email_regex, value):
                error_messages.append("Invalid email format.")
            elif field == "Phone Number" and not re.match(phone_regex, value):
                error_messages.append("Invalid phone number format.")
        if error_messages:
            messagebox.showerror("Validation Error", "\n".join(error_messages))
            return False
        return True

    def save_profile(self):
        if not self.validate_fields():
            return
        profile_data = {
            'Profile Name': self.entries['Profile Name'].get(),
            'First Name': self.entries['First Name'].get(),
            'Last Name': self.entries['Last Name'].get(),
            'Email': self.entries['Email'].get(),
            'Address Line': self.entries['Address Line'].get(),
            'City': self.entries['City'].get(),
            'State': self.entries['State'].get(),
            'Postal Code': self.entries['Postal Code'].get(),
            'Phone Number': self.encrypt_data(self.entries['Phone Number'].get()),
            'Card Number': self.encrypt_data(self.entries['Card Number'].get()),
            'Expiration Date': self.encrypt_data(self.entries['Expiration Date'].get()),
            'CVV': self.encrypt_data(self.entries['CVV'].get())
        }
        try:
            with open('user_profiles.json', 'r') as file:
                profiles = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            profiles = []
        if any(p['Profile Name'] == profile_data['Profile Name'] for p in profiles):
            messagebox.showerror("Duplicate Profile",
                                 "A profile with this name already exists. Please choose a different name.")
            return
        profiles.append(profile_data)
        with open('user_profiles.json', 'w') as file:
            json.dump(profiles, file, indent=4)
        messagebox.showinfo("Success", "Profile saved successfully!")
        self.profile_window.destroy()
        self.load_profiles()
        self.entries.clear()

    def encrypt_data(self, data):
        try:
            data_bytes = data.encode('utf-8')
            encrypted_bytes = self.cipher.encrypt(data_bytes)
            encrypted_base64 = base64.urlsafe_b64encode(encrypted_bytes)
            return encrypted_base64.decode('utf-8')
        except Exception as e:
            print(f"Encryption failed: {str(e)}")
            return None

    def decrypt_data(self, encrypted_data):
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            print(f"Decryption failed: {str(e)}")
            return None

    def print_decrypted_profiles(self):
        try:
            with open('user_profiles.json', 'r') as file:
                profiles = json.load(file)
            for profile in profiles:
                print("Profile Name:", profile['Profile Name'])
                print("First Name:", profile['First Name'])
                print("Email:", profile['Email'])
                print("Phone Number:", self.decrypt_data(profile['Phone Number']))
                print("Card Number:", self.decrypt_data(profile['Card Number']))
                print("Expiration Date:", self.decrypt_data(profile['Expiration Date']))
                print("CVV:", self.decrypt_data(profile['CVV']))
                print("---------")
        except Exception as e:
            print(f"Failed to load or decrypt profiles: {str(e)}")

    def delete_selected_profiles(self):
        try:
            with open('user_profiles.json', 'r') as file:
                profiles = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            profiles = []
        profiles = [p for p in profiles if not self.profile_vars[p['Profile Name']].get()]
        with open('user_profiles.json', 'w') as file:
            json.dump(profiles, file, indent=4)
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.load_profiles()
        messagebox.showinfo("Success", "Selected profiles have been deleted.")

    def edit_selected_profile(self):
        selected_profile_name = None
        for profile_name, var in self.profile_vars.items():
            if var.get() == 1:
                selected_profile_name = profile_name
                break
        if not selected_profile_name:
            messagebox.showerror("Error", "No profile selected for editing.")
            return
        self.open_edit_dialog(selected_profile_name)

    def open_edit_dialog(self, profile_name):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Profile")
        edit_window.geometry("350x475")
        edit_window.configure(background='#343746')
        try:
            with open('user_profiles.json', 'r') as file:
                profiles = json.load(file)
            profile_data = next((item for item in profiles if item['Profile Name'] == profile_name), None)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load the profile data: {str(e)}")
            return
        entries = {}
        row = 0
        for key, value in profile_data.items():
            if key in ['Phone Number', 'Card Number', 'CVV']:
                value = self.decrypt_data(value)
            label = tk.Label(edit_window, text=key, bg='#23272A', fg='white')
            label.grid(row=row, column=0, padx=10, pady=5)
            entry = tk.Entry(edit_window, width=30)
            entry.grid(row=row, column=1, padx=10, pady=5)
            if value:
                entry.insert(tk.END, value)
            entries[key] = entry
            row += 1
        save_button = tk.Button(edit_window, text="Save Changes",
                                command=lambda: self.save_changes(entries, profile_data, profiles, profile_name,
                                                                  edit_window), bg='#4B0082', fg='white')
        save_button.grid(row=row, column=1, padx=10, pady=20, sticky='e')

    def save_changes(self, entries, profile_data, profiles, profile_name, edit_window):
        for key, entry in entries.items():
            if key in ['Phone Number', 'Card Number', 'CVV']:
                profile_data[key] = self.encrypt_data(entry.get())
            else:
                profile_data[key] = entry.get()
        for i, profile in enumerate(profiles):
            if profile['Profile Name'] == profile_name:
                profiles[i] = profile_data
                break
        with open('user_profiles.json', 'w') as file:
            json.dump(profiles, file, indent=4)
        messagebox.showinfo("Success", "Profile updated successfully!")
        edit_window.destroy()
        self.load_profiles()
