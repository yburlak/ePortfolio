# login_window.py
# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Login window for user authentication

import tkinter as tk
from tkinter import ttk, messagebox
import services.auth_service

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.db = None
        
        # configure main window
        self.root.title("PetBag Boarding System - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.center_window()
        
        # style
        self.style = ttk.Style()
        self.style.configure('Login.TLabel', font=('Arial', 10))
        self.style.configure('Login.TButton', font=('Arial', 10, 'bold'))
        
        self.create_widgets()
    
    def center_window(self): # center the window on screen
        
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self): # create login form widgets
        
        # main frame
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # title
        title_label = ttk.Label(main_frame, text="🔐 PetBag Boarding System", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 30))
        
        # username field
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(username_frame, text="Username:", style='Login.TLabel').pack(anchor='w')
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(username_frame, textvariable=self.username_var, 
                                       font=('Arial', 11))
        self.username_entry.pack(fill=tk.X, pady=2)
        
        # password field
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(password_frame, text="Password:", style='Login.TLabel').pack(anchor='w')
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, 
                                       show="*", font=('Arial', 11))
        self.password_entry.pack(fill=tk.X, pady=2)
        
        # buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # login button
        login_btn = ttk.Button(button_frame, text="Login", 
                              command=self.login, style='Login.TButton')
        login_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # cancel button
        cancel_btn = ttk.Button(button_frame, text="Cancel", 
                               command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT)
        
        # bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())
        
        # set focus to username entry
        self.username_entry.focus()
    
    def set_database(self, db): # set database connection
        
        self.db = db
    
    def login(self): # handle login button click
        
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        if not self.db:
            messagebox.showerror("Error", "Database connection not available")
            return
        
        # authenticate user
        user, message = services.auth_service.AuthService.authenticate_user(self.db, username, password)
        
        if user:
            messagebox.showinfo("Success", message)
            self.root.destroy()
            self.on_login_success(user)
        else:
            messagebox.showerror("Error", message)
    
    def cancel(self): # handle cancel button click
        
        self.root.destroy()