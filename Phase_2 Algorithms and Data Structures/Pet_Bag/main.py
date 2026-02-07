# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Entry point and main window setup
# 2026-01-31: Refactored into MVC 

import tkinter as tk
from tkinter import messagebox
from database.connection import DatabaseConnection
import database.setup
from views import AppViews
from controllers import AppControllers

class PetBoardingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PetBag Boarding System")
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
        self.controllers = AppControllers(self.db)
        self.views = AppViews(self.root, self.controllers, self.db)
        self.controllers.set_views(self.views)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    root = tk.Tk()
    app = PetBoardingApp(root)
    app.run()

if __name__ == "__main__":
    main()