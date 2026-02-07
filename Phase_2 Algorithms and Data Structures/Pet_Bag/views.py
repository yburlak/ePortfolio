# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: All GUI widgets and layouts
# 2026-01-31: Refactored to implement UI and reporting tab

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class AppViews:
    def __init__(self, root, controllers, db):
        self.root = root
        self.controllers = controllers
        self.db = db
        self.create_header()
        self.create_tabs()
    
    # create application header with logo
    def create_header(self):
        
        title_frame = tk.Frame(self.root, bg="#f0f0f0", height=160)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        # try to load logo
        try:
            logo_img = tk.PhotoImage(file="BP_logo_small.png")
            logo_label = tk.Label(title_frame, image=logo_img, bg="#f0f0f0")
            logo_label.image = logo_img
            logo_label.place(x=10, y=10)
            
            title_label = tk.Label(title_frame, text="Pet Boarding & Grooming System", 
                                  font=("Arial", 20, "bold"), bg="#f0f0f0")
            title_label.place(relx=0.5, y=90, anchor="center")
            
            dashboard_label = tk.Label(title_frame, text="🏠 Dashboard", 
                                      font=("Arial", 14), bg="#f0f0f0")
            dashboard_label.place(relx=0.5, y=130, anchor="center")
            
        except Exception as e:
            print(f"Could not load logo image: {e}")
            title_frame.config(height=100)
            
            logo_label = tk.Label(title_frame, text="PetBag", 
                                 font=("Arial", 16, "bold"), bg="#f0f0f0", 
                                 justify="center", fg="#2196F3")
            logo_label.place(x=10, y=10)
            
            title_label = tk.Label(title_frame, text="Pet Boarding & Grooming System", 
                                  font=("Arial", 20, "bold"), bg="#f0f0f0")
            title_label.place(relx=0.5, y=15, anchor="center")
            
            dashboard_label = tk.Label(title_frame, text="🏠 Dashboard", 
                                      font=("Arial", 14), bg="#f0f0f0")
            dashboard_label.place(relx=0.5, y=45, anchor="center")
    

    #create main notebook with tabs
    def create_tabs(self):
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create all tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.pets_tab = ttk.Frame(self.notebook)
        self.customers_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        
        self.create_dashboard_section(self.dashboard_tab)
        self.create_pet_section(self.pets_tab)
        self.create_customer_section(self.customers_tab)
        self.create_reports_section(self.reports_tab)
        
        # Add to notebook
        self.notebook.add(self.dashboard_tab, text="Home")
        self.notebook.add(self.pets_tab, text="Pets")
        self.notebook.add(self.customers_tab, text="Customers")
        self.notebook.add(self.reports_tab, text="Reports")
    
    def create_dashboard_section(self, parent):
        main_content = tk.Frame(parent)
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_panel = tk.Frame(main_content, relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10), pady=10, ipadx=20)
        
        right_panel = tk.Frame(main_content, relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10, ipadx=20)
        
        self.create_available_spaces_section(left_panel)
        self.create_actions_section(right_panel)
    
    def create_available_spaces_section(self, parent):
        header_frame = tk.Frame(parent, bg="#e8f4fc")
        header_frame.pack(fill=tk.X, pady=(10, 20))
        
        tk.Label(header_frame, text="Available Spaces", 
                font=("Arial", 16, "bold"), bg="#e8f4fc").pack(pady=10)
        
        spaces = self.controllers.get_available_spaces()
        
        dog_frame = tk.Frame(parent, padx=20, pady=15)
        dog_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(dog_frame, text="🐶", font=("Arial", 24)).pack(side=tk.LEFT, padx=(0, 10))
        
        dog_info_frame = tk.Frame(dog_frame)
        dog_info_frame.pack(side=tk.LEFT)
        
        tk.Label(dog_info_frame, text="Dogs:", font=("Arial", 14, "bold")).pack(anchor="w")

        self.dog_spaces_label = tk.Label(dog_info_frame, 
                                        text=f"Available: {spaces['dog_spaces']} of 30",
                                        font=("Arial", 12))
        self.dog_spaces_label.pack(anchor="w")
        
        cat_frame = tk.Frame(parent, padx=20, pady=15)
        cat_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(cat_frame, text="🐱", font=("Arial", 24)).pack(side=tk.LEFT, padx=(0, 10))
        
        cat_info_frame = tk.Frame(cat_frame)
        cat_info_frame.pack(side=tk.LEFT)
        
        tk.Label(cat_info_frame, text="Cats:", font=("Arial", 14, "bold")).pack(anchor="w")

        self.cat_spaces_label = tk.Label(cat_info_frame, 
                                        text=f"Available: {spaces['cat_spaces']} of 12",
                                        font=("Arial", 12))
        self.cat_spaces_label.pack(anchor="w")
        
        tk.Frame(parent, height=20).pack()
    
    def create_actions_section(self, parent):
        header_frame = tk.Frame(parent, bg="#f0f8f0")
        header_frame.pack(fill=tk.X, pady=(10, 20))
        
        tk.Label(header_frame, text="Quick Actions", 
                font=("Arial", 16, "bold"), bg="#f0f8f0").pack(pady=10)
        
        actions_container = tk.Frame(parent)
        actions_container.pack(expand=True)
        
        booking_frame = tk.Frame(actions_container)
        booking_frame.pack(pady=15)
        
        tk.Label(booking_frame, text="📅", font=("Arial", 32)).pack(side=tk.LEFT, padx=(0, 15))
        
        booking_btn_frame = tk.Frame(booking_frame)
        booking_btn_frame.pack(side=tk.LEFT)
        
        tk.Label(booking_btn_frame, text="New Booking", 
                font=("Arial", 12, "bold")).pack(anchor="w")
        
        tk.Button(booking_btn_frame, text="Check-In", 
                 command=self.controllers.show_checkin_form,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 padx=30, pady=10, width=12).pack(pady=5)
        
        endstay_frame = tk.Frame(actions_container)
        endstay_frame.pack(pady=15)
        
        tk.Label(endstay_frame, text="⏰", font=("Arial", 32)).pack(side=tk.LEFT, padx=(0, 15))
        
        endstay_btn_frame = tk.Frame(endstay_frame)
        endstay_btn_frame.pack(side=tk.LEFT)
        
        tk.Label(endstay_btn_frame, text="End Stay", 
                font=("Arial", 12, "bold")).pack(anchor="w")
        
        tk.Button(endstay_btn_frame, text="Check-Out", 
                 command=self.controllers.show_checkout_form,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 padx=30, pady=10, width=12).pack(pady=5)
    
    def create_pet_section(self, parent):
        header_frame = tk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(10, 10))
        
        tk.Label(header_frame, text="🐕", font=("Arial", 20)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(header_frame, text="Pet Management", 
                font=("Arial", 24, "bold")).pack(side=tk.LEFT)
        
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="Add Pet", command=self.controllers.add_pet,
                 bg="#2196F3", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="Delete Pet", command=self.controllers.delete_pet,
                 bg="#FF5722", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))
        
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ("ID", "Name", "Type", "Age", "Breed", "Owner")
        self.pet_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.pet_tree.heading(col, text=col)
            self.pet_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.pet_tree.yview)
        self.pet_tree.configure(yscrollcommand=scrollbar.set)
        
        self.pet_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.pet_tree.bind("<Double-1>", self.controllers.edit_pet)
    
    def create_customer_section(self, parent):
        header_frame = tk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(10, 10))
        
        tk.Label(header_frame, text="👥", font=("Arial", 20)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(header_frame, text="Customer Management", 
                font=("Arial", 24, "bold")).pack(side=tk.LEFT)
        
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="Add Customer", command=self.controllers.add_customer,
                 bg="#2196F3", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="Delete Customer", command=self.controllers.delete_customer,
                 bg="#FF5722", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))
        
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ("ID", "First Name", "Last Name", "Phone", "Email")
        self.customer_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.customer_tree.bind("<Double-1>", self.controllers.edit_customer)
    
    def create_reports_section(self, parent):
        main_frame = tk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title_frame = tk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(title_frame, text="📊", font=("Arial", 20)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(title_frame, text="Reports Dashboard", 
                font=("Arial", 24, "bold")).pack(side=tk.LEFT)
        
        period_frame = tk.Frame(main_frame)
        period_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(period_frame, text="Report Period:", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.report_period = tk.StringVar(value="30")
        period_combo = ttk.Combobox(period_frame, textvariable=self.report_period, 
                                   values=["7", "30", "60", "90"], 
                                   state="readonly", width=10)
        period_combo.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(period_frame, text="days").pack(side=tk.LEFT)
        
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Button(buttons_frame, text="📈 Generate Occupancy Report", 
                 command=self.generate_occupancy_report,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 padx=20, pady=10, width=22).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Button(buttons_frame, text="💰 Generate Revenue Report", 
                 command=self.generate_revenue_report,
                 bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                 padx=20, pady=10, width=22).pack(side=tk.LEFT)
        
        # create a container frame for report output and buttons
        output_container = tk.Frame(main_frame)
        output_container.pack(fill=tk.BOTH, expand=True)
        
        # create frame for text widget
        text_frame = tk.LabelFrame(output_container, text="Report Output", padx=10, pady=10)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # create frame for vertical buttons
        button_column = tk.Frame(output_container)
        button_column.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        
        # text widget for report output 
        self.report_text = tk.Text(text_frame, wrap=tk.WORD, height=18, 
                                  font=("Courier New", 9))
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar.set)
        
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # create vertical buttons with consistent styling
        button_style = {
            'font': ("Arial", 10, "bold"),
            'padx': 20,
            'pady': 12,
            'width': 15
        }
        
        clear_btn = tk.Button(button_column, text="🗑️ Clear Report", 
                             command=self.clear_report,
                             bg="#FF9800", fg="white", **button_style)
        clear_btn.pack(pady=(0, 10))
        
        save_btn = tk.Button(button_column, text="💾 Save to File", 
                            command=self.save_report,
                            bg="#2196F3", fg="white", **button_style)
        save_btn.pack(pady=(0, 10))
        
        print_btn = tk.Button(button_column, text="🖨️ Print to Console", 
                             command=self.print_report,
                             bg="#9C27B0", fg="white", **button_style)
        print_btn.pack()
        
        # add some padding at the bottom
        tk.Frame(main_frame, height=10).pack()
    
    def generate_occupancy_report(self):
        self.controllers.generate_occupancy_report(int(self.report_period.get()))
    
    def generate_revenue_report(self):
        self.controllers.generate_revenue_report(int(self.report_period.get()))
    
    def display_report(self, report):
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)
    
    def clear_report(self):
        self.report_text.delete(1.0, tk.END)
    
    def save_report(self):
        report = self.report_text.get(1.0, tk.END)
        if not report.strip():
            messagebox.showwarning("Warning", "No report to save")
            return
        
        filename = f"petbag_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w') as f:
                f.write(report)
            messagebox.showinfo("Success", f"Report saved as:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {str(e)}")
    
    def print_report(self):
        report = self.report_text.get(1.0, tk.END)
        if not report.strip():
            messagebox.showwarning("Warning", "No report to print")
            return
        
        print("="*80)
        print("PET BAG BOARDING SYSTEM - REPORT")
        print("="*80)
        print(report)
        print("="*80)
        messagebox.showinfo("Print", "Report sent to console (check terminal)")
    
    def update_dashboard(self):
        self.controllers.update_dashboard()