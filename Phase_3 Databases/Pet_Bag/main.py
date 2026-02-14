# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Entry point and main window setup
# 2026-01-31: Refactored into MVC 
# 2026-02-07: Added authentication system

import tkinter as tk
from tkinter import messagebox
from database.connection import DatabaseConnection
import database.setup
from views import AppViews
import services.auth_service

class PetBoardingApp:
    def __init__(self, root, current_user):
        self.root = root
        self.current_user = current_user
        self.root.title(f"PetBag Boarding System - Welcome {current_user['first_name']}")
        self.root.geometry("1000x600")
        
        # setup database
        try:
            database.setup.setup_database()
            self.db = DatabaseConnection()
            
            if not self.db.connect(database="pet_bag_db"):
                messagebox.showerror("Error", "Cannot connect to database")
                root.destroy()
                return
        except Exception as e:
            messagebox.showerror("Error", f"Database setup failed: {str(e)}")
            root.destroy()
            return
        
        # initialize controllers and views
        from controllers import AppControllers
        self.controllers = AppControllers(self.db, self.current_user)
        self.views = AppViews(self.root, self.controllers, self.db, self.current_user)
        self.controllers.set_views(self.views)
    
    def run(self): #start the app
        
        self.root.mainloop()

def main():
    # create login window first
    login_root = tk.Tk()
    
    def on_login_success(user):
        # create main application window after successful login
        main_root = tk.Tk()
        app = PetBoardingApp(main_root, user)
        app.run()
    
    # setup database for login
    try:
        database.setup.setup_database()
        db = DatabaseConnection()
        
        if not db.connect(database="pet_bag_db"):
            messagebox.showerror("Error", "Cannot connect to database")
            login_root.destroy()
            return
        
        # import and create login window
        from login_window import LoginWindow
        login_window = LoginWindow(login_root, on_login_success)
        login_window.set_database(db)
        login_root.mainloop()
        
        db.disconnect()
        
    except Exception as e:
        messagebox.showerror("Error", f"Application startup failed: {str(e)}")
        login_root.destroy()

if __name__ == "__main__":
    main()