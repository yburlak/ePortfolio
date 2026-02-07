# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: TKinter GUI for PetBag Application with input validations and error handling

# import libraries and modules:
import tkinter as tk  
from tkinter import ttk, messagebox  # for widgets and dialogs
from database.connection import DatabaseConnection  # for db connection
from models.customer import Customer  # use customer model
from models.pet import Pet  # use pet model
import database.setup  # db setup
from services.boarding_service import BoardingService  
from services.checkout_service import CheckoutService  
from datetime import datetime  # for date/time

class PetBoardingApp:
    def __init__(self, root):  # initialize app
        self.root = root  # main window
        self.root.title("PetBag Boarding System")  
        self.root.geometry("1000x600")  # window dimensions
        
        database.setup.setup_database()
        
        # connect to pet_bag_db
        self.db = DatabaseConnection()

        # if no connection -> show error and close
        if not self.db.connect(database="pet_bag_db"):
            messagebox.showerror("Error", "Cannot connect to database")
            root.destroy()  
            return
        
        # create layout and tabs
        self.create_main_layout()
        self.create_tabs()
        
        # load data from db into tabs
        self.load_customers()
        self.load_pets()
    
    def create_main_layout(self):  # main screen layout
        title_frame = tk.Frame(self.root, bg="#f0f0f0", height=160)
        title_frame.pack(fill=tk.X, padx=10, pady=10)  
        title_frame.pack_propagate(False)  
        
        # load logo image into left upper corner
        try:
            logo_img = tk.PhotoImage(file="BP_logo_small.png")
            
            logo_label = tk.Label(title_frame, image=logo_img, bg="#f0f0f0")
            logo_label.image = logo_img  
            
            logo_label.place(x=10, y=10)
            
            title_label = tk.Label(title_frame, text="Pet Boarding & Grooming System", 
                                  font=("Arial", 20, "bold"), bg="#f0f0f0")
            title_label.place(relx=0.5, y=90, anchor="center")  
            
            # dashboard emoji and label
            dashboard_label = tk.Label(title_frame, text="🏠 Dashboard", 
                                      font=("Arial", 14), bg="#f0f0f0")
            dashboard_label.place(relx=0.5, y=130, anchor="center")
            
        except Exception as e:
            # if image failed to load use text "PetBag"
            print(f"Could not load logo image: {e}")
            title_frame.config(height=100) 
            
            logo_label = tk.Label(title_frame, text="PetBag", 
                                 font=("Arial", 16, "bold"), bg="#f0f0f0", 
                                 justify="center", fg="#2196F3")
            logo_label.place(x=10, y=10)
            
            title_label = tk.Label(title_frame, text="Pet Boarding & Grooming System", 
                                  font=("Arial", 20, "bold"), bg="#f0f0f0")
            title_label.place(relx=0.5, y=15, anchor="center")
            
            # dashboard emoji and label
            dashboard_label = tk.Label(title_frame, text="🏠 Dashboard", 
                                      font=("Arial", 14), bg="#f0f0f0")
            dashboard_label.place(relx=0.5, y=45, anchor="center")
    
    def create_tabs(self):  # create tabs
        # create notebook widget for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 1. Home for check-in & check-out
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Home")
        self.create_dashboard_section(self.dashboard_tab)
        
        # 2. Pets for pet records management
        self.pets_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.pets_tab, text="Pets")
        self.create_pet_section(self.pets_tab)
        
        # 3. Customers for customer records management
        self.customers_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_tab, text="Customers")
        self.create_customer_section(self.customers_tab)
        
        # 4. Reports for placeholder Coming Soon
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports")
        self.create_reports_section(self.reports_tab)
    
    def create_dashboard_section(self, parent):  # creates Home Tab view split in two parts
        main_content = tk.Frame(parent)
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # left part: available spaces
        left_panel = tk.Frame(main_content, relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10), pady=10, ipadx=20)
        
        # right part: actions
        right_panel = tk.Frame(main_content, relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10, ipadx=20)
        
        # show available dog/cat spaces
        self.create_available_spaces_section(left_panel)
        
        # show check-in/check-out buttons 
        self.create_actions_section(right_panel)
    
    def create_available_spaces_section(self, parent):  # get available spaces from boarding_service and displays them
        
        header_frame = tk.Frame(parent, bg="#e8f4fc")
        header_frame.pack(fill=tk.X, pady=(10, 20))
        
        tk.Label(header_frame, text="Available Spaces", 
                font=("Arial", 16, "bold"), bg="#e8f4fc").pack(pady=10)
        
        spaces = BoardingService.get_available_spaces()
        
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
    
    def create_actions_section(self, parent):  # create action buttons with emojis
        header_frame = tk.Frame(parent, bg="#f0f8f0")
        header_frame.pack(fill=tk.X, pady=(10, 20))
        
        tk.Label(header_frame, text="Quick Actions", 
                font=("Arial", 16, "bold"), bg="#f0f8f0").pack(pady=10)
        
        actions_container = tk.Frame(parent)
        actions_container.pack(expand=True)
        
        # new booking/check-in action 
        booking_frame = tk.Frame(actions_container)
        booking_frame.pack(pady=15)
        
        tk.Label(booking_frame, text="📅", font=("Arial", 32)).pack(side=tk.LEFT, padx=(0, 15))
        
        booking_btn_frame = tk.Frame(booking_frame)
        booking_btn_frame.pack(side=tk.LEFT)
        
        tk.Label(booking_btn_frame, text="New Booking", 
                font=("Arial", 12, "bold")).pack(anchor="w")
        # click opens check-in form
        tk.Button(booking_btn_frame, text="Check-In", 
                 command=self.show_checkin_form,  # callback function
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 padx=30, pady=10, width=12).pack(pady=5)
        
        # end stay/check-out action
        endstay_frame = tk.Frame(actions_container)
        endstay_frame.pack(pady=15)
        
        tk.Label(endstay_frame, text="⏰", font=("Arial", 32)).pack(side=tk.LEFT, padx=(0, 15))
        
        endstay_btn_frame = tk.Frame(endstay_frame)
        endstay_btn_frame.pack(side=tk.LEFT)
        
        tk.Label(endstay_btn_frame, text="End Stay", 
                font=("Arial", 12, "bold")).pack(anchor="w")
        # open check-out form
        tk.Button(endstay_btn_frame, text="Check-Out", 
                 command=self.show_checkout_form,  # callback function
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 padx=30, pady=10, width=12).pack(pady=5)
    
    def create_pet_section(self, parent):  # create pet tab with emoji
        header_frame = tk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(10, 10))
        
        tk.Label(header_frame, text="🐕", font=("Arial", 20)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(header_frame, text="Pet Management", 
                font=("Arial", 24, "bold")).pack(side=tk.LEFT)
        
        # add pet button
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="Add Pet", command=self.add_pet,
                 bg="#2196F3", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))
        
        # pet list displayed via table
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # pet table columns
        columns = ("ID", "Name", "Type", "Age", "Breed", "Owner")
        self.pet_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.pet_tree.heading(col, text=col)
            self.pet_tree.column(col, width=150)
        
        # add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.pet_tree.yview)
        self.pet_tree.configure(yscrollcommand=scrollbar.set)
        
        self.pet_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # uses double-click for pet data editing
        self.pet_tree.bind("<Double-1>", self.edit_pet)
    
    def create_customer_section(self, parent):  # create customer tab with emoji
        header_frame = tk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(10, 10))
        
        tk.Label(header_frame, text="👥", font=("Arial", 20)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(header_frame, text="Customer Management", 
                font=("Arial", 24, "bold")).pack(side=tk.LEFT)
        
        # add customer button
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="Add Customer", command=self.add_customer,
                 bg="#2196F3", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))
        
        # customer list display via table
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # customer table columns
        columns = ("ID", "First Name", "Last Name", "Phone", "Email")
        self.customer_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=150)
        
        # add scrollbar 
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # uses double-click for customer data editing
        self.customer_tree.bind("<Double-1>", self.edit_customer)
    
    def create_reports_section(self, parent):  # create report tab with Coming Soon message
        center_frame = tk.Frame(parent)
        center_frame.pack(fill=tk.BOTH, expand=True)
        
        # serve as placeholder 
        tk.Label(center_frame, text="Coming Soon", 
                font=("Arial", 32, "bold"), fg="#666").pack(expand=True)
    
    def load_customers(self):  # load all customer data
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        try:
            # get all customer records from db
            customers = Customer.get_all(self.db)
            if customers:
                # inserts each customer into each row
                for cust in customers:
                    self.customer_tree.insert("", tk.END, values=(
                        cust['customer_id'],
                        cust['first_name'],
                        cust['last_name'],
                        cust['phone'] or "",  
                        cust['email'] or ""
                    ))
            else:
                print("No customers found in database")
        except Exception as e:
            # if couldn't load -> error message
            print(f"Error loading customers: {e}")
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")
    
    def load_pets(self):  # load all pet data
        for item in self.pet_tree.get_children():
            self.pet_tree.delete(item)
        
        try:
            # get all pet records from db
            pets = Pet.get_all(self.db)
            if pets:
                # insert each pet record as a row 
                for pet in pets:
                    # create owner display name from first and last name
                    owner = f"{pet['first_name']} {pet['last_name']}"
                    self.pet_tree.insert("", tk.END, values=(
                        pet['pet_id'],
                        pet['pet_name'],
                        pet['pet_type'],
                        pet['pet_age'],
                        pet['breed'] or "",  
                        owner
                    ))
            else:
                print("No pets found in database")
        except Exception as e:
            # if couldn't load -> error message
            print(f"Error loading pets: {e}")
            messagebox.showerror("Error", f"Failed to load pets: {str(e)}")
    
    def show_checkin_form(self):  # create new booking/check-in window
        dialog = tk.Toplevel(self.root)
        dialog.title("New Booking - Check-In")
        dialog.geometry("600x400")
        dialog.resizable(False, False)  
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # owner field
        tk.Label(left_frame, text="Owner:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        owner_entry = tk.Entry(left_frame, width=28)
        owner_entry.pack(anchor="w", pady=(0, 15))
        
        # pet type dog/cat
        tk.Label(left_frame, text="Pet Type:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        pet_type_var = tk.StringVar(value="Dog")  
        pet_type_combo = ttk.Combobox(left_frame, textvariable=pet_type_var, 
                                     values=["Dog", "Cat"], state="readonly", width=25)
        pet_type_combo.pack(anchor="w", pady=(0, 15))
        
        # pet name field
        tk.Label(left_frame, text="Pet Name:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        pet_name_entry = tk.Entry(left_frame, width=28)
        pet_name_entry.pack(anchor="w", pady=(0, 15))
        
        # grooming checkbox
        grooming_var = tk.BooleanVar() 
        tk.Checkbutton(left_frame, text="Grooming Requested", 
                      variable=grooming_var, font=("Arial", 11)).pack(anchor="w", pady=15)
        
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # breed field
        tk.Label(right_frame, text="Breed:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        breed_entry = tk.Entry(right_frame, width=28)
        breed_entry.pack(anchor="w", pady=(0, 15))
        
        # age dropdown from 1 to 16 y.o., default 1 y.o.
        tk.Label(right_frame, text="Age:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        age_values = [str(i) for i in range(1, 17)]  
        age_var = tk.StringVar(value="1")  
        age_combo = ttk.Combobox(right_frame, textvariable=age_var, 
                                values=age_values, state="readonly", width=25)
        age_combo.pack(anchor="w", pady=(0, 15))
        
        # weight field 
        tk.Label(right_frame, text="Weight:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        weight_frame = tk.Frame(right_frame)
        weight_frame.pack(anchor="w", pady=(0, 15))
        
        weight_entry = tk.Entry(weight_frame, width=10)
        weight_entry.pack(side=tk.LEFT)
        tk.Label(weight_frame, text=" lbs").pack(side=tk.LEFT, padx=(5, 0))
        
        # days stay dropdown from 1 - 31 days, default 1 day
        tk.Label(right_frame, text="Days Stay:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        days_values = [str(i) for i in range(1, 32)]  
        days_var = tk.StringVar(value="1")  
        days_combo = ttk.Combobox(right_frame, textvariable=days_var, 
                                 values=days_values, state="readonly", width=25)
        days_combo.pack(anchor="w", pady=(0, 15))
        

        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def check_in():  # process and validate check-in form
            # validate all entry fields
            if not pet_name_entry.get().strip():
                messagebox.showerror("Error", "Please enter pet name")
                return
            
            if not owner_entry.get().strip():
                messagebox.showerror("Error", "Please enter owner name")
                return
            
            if not breed_entry.get().strip():
                messagebox.showerror("Error", "Please enter breed")
                return
            
            try:
                pet_type = pet_type_var.get()
                pet_name = pet_name_entry.get().strip()
                owner_name = owner_entry.get().strip()
                breed = breed_entry.get().strip()
                age = int(age_var.get()) 
                days_stay = int(days_var.get())
                # handle optional weight field
                weight = float(weight_entry.get()) if weight_entry.get() else 0
                grooming = grooming_var.get()
                
                # check if customer exists
                customers = Customer.get_all(self.db)
                customer_exists = False
                customer_id = None
                
                # search for existing customer by name 
                for cust in customers:
                    full_name = f"{cust['first_name']} {cust['last_name']}"
                    if owner_name.lower() in full_name.lower():
                        customer_exists = True
                        customer_id = cust['customer_id']
                        break
                
                # create new customer if doesn't exist
                if not customer_exists:
                    # split owner name into two parts
                    name_parts = owner_name.split()
                    first_name = name_parts[0] if len(name_parts) > 0 else owner_name
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
                    
                    # create customer record
                    customer_data = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'phone': '',
                        'email': ''
                    }
                    customer_id = Customer.create(self.db, customer_data)
                
                # create pet record
                pet_data = {
                    'customer_id': customer_id,
                    'pet_name': pet_name,
                    'pet_type': pet_type,
                    'pet_age': age,
                    'breed': breed,
                    'weight': weight
                }
                pet_id = Pet.create(self.db, pet_data)
                
                # check in the pet using boarding_service
                success, message = BoardingService.check_in_pet(
                    self.db, pet_id, days_stay, grooming
                )
                
                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()  # close dialog
                    # refresh UI 
                    self.update_dashboard()
                    self.load_pets()
                    self.load_customers()
                else:
                    messagebox.showerror("Error", message)
                    
            except ValueError as e:
                # handle all errors
                messagebox.showerror("Error", f"Please enter valid data: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        # check-in button for processing and validation
        tk.Button(buttons_frame, text="Check-In", command=check_in,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 padx=30, pady=10).pack(side=tk.RIGHT, padx=(10, 0))
        
        # cancel button to make no changes
        tk.Button(buttons_frame, text="Cancel", command=dialog.destroy,
                 bg="#FF9800", fg="white", font=("Arial", 11),
                 padx=30, pady=10).pack(side=tk.RIGHT)
    
    def show_checkout_form(self):  # create check-out form
        dialog = tk.Toplevel(self.root)
        dialog.title("Check-Out")
        dialog.geometry("500x500")
        dialog.resizable(False, False)  
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Select Pet:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))
        
        # get current boardings from boarding_service
        boardings = BoardingService.get_current_boardings(self.db)
        # dropdown list 
        boarding_list = [f"{b['pet_name']} (Owner: {b['first_name']} {b['last_name']})" for b in boardings]
        
        pet_var = tk.StringVar()  
        pet_combo = ttk.Combobox(main_frame, textvariable=pet_var, 
                                values=boarding_list, state="readonly", width=40)
        pet_combo.pack(anchor="w", pady=(0, 20))
        
        # fill out form with pet data
        details_frame = tk.LabelFrame(main_frame, text="Pet Details", padx=10, pady=10)
        details_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.pet_name_label = tk.Label(details_frame, text="Pet Name: ", anchor="w")
        self.pet_name_label.pack(fill=tk.X, pady=2)
        
        self.owner_label = tk.Label(details_frame, text="Owner: ", anchor="w")
        self.owner_label.pack(fill=tk.X, pady=2)
        
        self.days_label = tk.Label(details_frame, text="Boarding Days: ", anchor="w")
        self.days_label.pack(fill=tk.X, pady=2)
        
        self.grooming_label = tk.Label(details_frame, text="Grooming: ", anchor="w")
        self.grooming_label.pack(fill=tk.X, pady=2)
        
        # total amount
        amount_frame = tk.LabelFrame(main_frame, text="Payment", padx=10, pady=10)
        amount_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.amount_label = tk.Label(amount_frame, text="Total Amount Due: $0.00", 
                                    font=("Arial", 12, "bold"))
        self.amount_label.pack(anchor="w")
        
        # buttons 
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        def calculate_total():  # calculate services total
            selection = pet_combo.get()
            if selection and boardings:
                for b in boardings:
                    display_name = f"{b['pet_name']} (Owner: {b['first_name']} {b['last_name']})"
                    if display_name == selection:
                        # use amount from database
                        total = b['amount_due']
                        self.amount_label.config(text=f"Total Amount Due: ${total:.2f}")
                        
                        # update details
                        self.pet_name_label.config(text=f"Pet Name: {b['pet_name']}")
                        self.owner_label.config(text=f"Owner: {b['first_name']} {b['last_name']}")
                        self.days_label.config(text=f"Boarding Days: {b['days_stay']}")
                        self.grooming_label.config(text=f"Grooming: {'Yes' if b['grooming_requested'] else 'No'}")
                        break
        
        def confirm_checkout():  # process check-out
            selection = pet_combo.get()
            if not selection:
                messagebox.showerror("Error", "Please select a pet")
                return
            
            response = messagebox.askyesno("Confirm Check-out", 
                                          f"Check out {selection.split('(')[0].strip()}?")
            if response:
                # find boarding ID 
                for b in boardings:
                    display_name = f"{b['pet_name']} (Owner: {b['first_name']} {b['last_name']})"
                    if display_name == selection:
                        # use checkout_service
                        success, message, amount = CheckoutService.check_out_pet(self.db, b['boarding_id'])
                        if success:
                            # show invoice after successful check-out
                            invoice = CheckoutService.generate_invoice(self.db, b['boarding_id'])
                            if invoice:
                                invoice_dialog = tk.Toplevel(dialog)
                                invoice_dialog.title("Invoice")
                                invoice_dialog.geometry("400x500")
                                
                                text_widget = tk.Text(invoice_dialog, wrap=tk.WORD)
                                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                                text_widget.insert(1.0, invoice)
                                text_widget.config(state=tk.DISABLED)
                            
                            messagebox.showinfo("Success", message)
                            dialog.destroy()  # close check-out dialog
                            self.update_dashboard()  # refresh
                        else:
                            messagebox.showerror("Error", message)
                        break
        
        def generate_invoice():  # create and display invoice
            selection = pet_combo.get()
            if not selection:
                messagebox.showerror("Error", "Please select a pet")
                return
            
            # find selected boarding and create invoice
            for b in boardings:
                display_name = f"{b['pet_name']} (Owner: {b['first_name']} {b['last_name']})"
                if display_name == selection:
                    invoice = CheckoutService.generate_invoice(self.db, b['boarding_id'])
                    if invoice:
                        # display invoice in new window
                        invoice_dialog = tk.Toplevel(dialog)
                        invoice_dialog.title("Invoice")
                        invoice_dialog.geometry("400x500")
                        
                        text_widget = tk.Text(invoice_dialog, wrap=tk.WORD)
                        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                        text_widget.insert(1.0, invoice)
                        text_widget.config(state=tk.DISABLED) 
                    break
        
        # calculate total button
        tk.Button(buttons_frame, text="Calculate Total", command=calculate_total,
                 bg="#2196F3", fg="white", font=("Arial", 10),
                 padx=15, pady=8).pack(side=tk.LEFT, padx=(0, 5))
        
        # confirm check-out button
        tk.Button(buttons_frame, text="Confirm Check-out", command=confirm_checkout,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        # invoice button 
        tk.Button(buttons_frame, text="Invoice", command=generate_invoice,
                 bg="#2196F3", fg="white", font=("Arial", 10),
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        # cancel button
        tk.Button(buttons_frame, text="Cancel", command=dialog.destroy,
                 bg="#FF9800", fg="white", font=("Arial", 10),
                 padx=15, pady=8).pack(side=tk.RIGHT)
    
    def update_dashboard(self):  # refresh dashboard with current space counts
        spaces = BoardingService.get_available_spaces()
    
        self.dog_spaces_label.config(text=f"Available: {spaces['dog_spaces']} of 30")
        self.cat_spaces_label.config(text=f"Available: {spaces['cat_spaces']} of 12")
    
    def add_customer(self):  # display dialog to add new customer
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Customer")
        dialog.geometry("400x300")
        
        tk.Label(dialog, text="First Name:", font=("Arial", 11)).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        first_name_entry = tk.Entry(dialog, width=30)
        first_name_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(dialog, text="Last Name:", font=("Arial", 11)).grid(row=1, column=0, pady=10, padx=10, sticky="w")
        last_name_entry = tk.Entry(dialog, width=30)
        last_name_entry.grid(row=1, column=1, pady=10, padx=10)
        
        tk.Label(dialog, text="Phone:", font=("Arial", 11)).grid(row=2, column=0, pady=10, padx=10, sticky="w")
        phone_entry = tk.Entry(dialog, width=30)
        phone_entry.grid(row=2, column=1, pady=10, padx=10)
        
        tk.Label(dialog, text="Email:", font=("Arial", 11)).grid(row=3, column=0, pady=10, padx=10, sticky="w")
        email_entry = tk.Entry(dialog, width=30)
        email_entry.grid(row=3, column=1, pady=10, padx=10)
        
        def save_customer():  # save new customer data with validation
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            
            if not first_name:
                messagebox.showerror("Error", "First name is required")
                return
            
            customer_data = {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone_entry.get().strip(),
                'email': email_entry.get().strip()
            }
            
            try:
                Customer.create(self.db, customer_data)
                messagebox.showinfo("Success", "Customer added successfully")
                dialog.destroy()  
                self.load_customers()  # refresh customer list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {str(e)}")
        
        # save button
        tk.Button(dialog, text="Save", command=save_customer,
                 bg="#2196F3", fg="white", padx=20, pady=10).grid(row=4, column=0, columnspan=2, pady=20)
    
    def edit_customer(self, event):  # enable editing of customer record via double-click
        selection = self.customer_tree.selection()
        if not selection:
            return  
        
        item = self.customer_tree.item(selection[0])
        customer_id = item['values'][0]  
        
        # get customer details from db
        customers = Customer.get_all(self.db)
        customer = None
        for cust in customers:
            if cust['customer_id'] == customer_id:
                customer = cust
                break
        
        if not customer:
            return  
        
        # create edit window
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Customer")
        dialog.geometry("400x300")
        
        # form fields with existing data 
        tk.Label(dialog, text="First Name:", font=("Arial", 11)).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        first_name_entry = tk.Entry(dialog, width=30)
        first_name_entry.insert(0, customer['first_name'])  
        first_name_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(dialog, text="Last Name:", font=("Arial", 11)).grid(row=1, column=0, pady=10, padx=10, sticky="w")
        last_name_entry = tk.Entry(dialog, width=30)
        last_name_entry.insert(0, customer['last_name'])
        last_name_entry.grid(row=1, column=1, pady=10, padx=10)
        
        tk.Label(dialog, text="Phone:", font=("Arial", 11)).grid(row=2, column=0, pady=10, padx=10, sticky="w")
        phone_entry = tk.Entry(dialog, width=30)
        phone_entry.insert(0, customer['phone'] or "")  
        phone_entry.grid(row=2, column=1, pady=10, padx=10)
        
        tk.Label(dialog, text="Email:", font=("Arial", 11)).grid(row=3, column=0, pady=10, padx=10, sticky="w")
        email_entry = tk.Entry(dialog, width=30)
        email_entry.insert(0, customer['email'] or "") 
        email_entry.grid(row=3, column=1, pady=10, padx=10)
        
        def update_customer():  # update customer data
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            
            # validate required field
            if not first_name:
                messagebox.showerror("Error", "First name is required")
                return
            
            customer_data = {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone_entry.get().strip(),
                'email': email_entry.get().strip()
            }
            
            try:
                # update customer in db
                Customer.update(self.db, customer_id, customer_data)
                messagebox.showinfo("Success", "Customer updated successfully")
                dialog.destroy()  
                self.load_customers()  # refresh customer list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update customer: {str(e)}")
        
        # update button
        tk.Button(dialog, text="Update", command=update_customer,
                 bg="#2196F3", fg="white", padx=20, pady=10).grid(row=4, column=0, columnspan=2, pady=20)
    
    def add_pet(self):  # create add new pet window
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Pet")
        dialog.geometry("400x400")
        
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # owner dropdown 
        tk.Label(content_frame, text="Owner:", font=("Arial", 11)).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        
        customers = Customer.get_all(self.db)
        customer_list = [f"{c['first_name']} {c['last_name']}" for c in customers]
        
        owner_combo = ttk.Combobox(content_frame, values=customer_list, state="readonly", width=25)
        owner_combo.grid(row=0, column=1, pady=10, padx=10)
        
        # pet type dropdown, default dog
        tk.Label(content_frame, text="Pet Type:", font=("Arial", 11)).grid(row=1, column=0, pady=10, padx=10, sticky="w")
        pet_type_var = tk.StringVar(value="Dog") 
        pet_type_combo = ttk.Combobox(content_frame, textvariable=pet_type_var, 
                                     values=["Dog", "Cat"], state="readonly", width=25)
        pet_type_combo.grid(row=1, column=1, pady=10, padx=10)
        
        # pet name field
        tk.Label(content_frame, text="Pet Name:", font=("Arial", 11)).grid(row=2, column=0, pady=10, padx=10, sticky="w")
        pet_name_entry = tk.Entry(content_frame, width=28)
        pet_name_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # breed field
        tk.Label(content_frame, text="Breed:", font=("Arial", 11)).grid(row=3, column=0, pady=10, padx=10, sticky="w")
        breed_entry = tk.Entry(content_frame, width=28)
        breed_entry.grid(row=3, column=1, pady=10, padx=10)
        
        # age dropdown from 1-16 y.o., default 1 y.o.
        tk.Label(content_frame, text="Age:", font=("Arial", 11)).grid(row=4, column=0, pady=10, padx=10, sticky="w")
        age_values = [str(i) for i in range(1, 17)]  
        age_var = tk.StringVar(value="1")  
        age_combo = ttk.Combobox(content_frame, textvariable=age_var, 
                                values=age_values, state="readonly", width=25)
        age_combo.grid(row=4, column=1, pady=10, padx=10)
        
        # weight field
        tk.Label(content_frame, text="Weight:", font=("Arial", 11)).grid(row=5, column=0, pady=10, padx=10, sticky="w")
        weight_entry = tk.Entry(content_frame, width=28)
        weight_entry.grid(row=5, column=1, pady=10, padx=10)
        
        # buttons frame at bottom
        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def save_pet():  # save new pet data with validation of fields
            if not owner_combo.get():
                messagebox.showerror("Error", "Please select an owner")
                return
            
            if not pet_name_entry.get().strip():
                messagebox.showerror("Error", "Pet name is required")
                return
            
            if not breed_entry.get().strip():
                messagebox.showerror("Error", "Breed is required")
                return
            
            try:
                selected_owner = owner_combo.get()
                customer_id = None
                for cust in customers:
                    full_name = f"{cust['first_name']} {cust['last_name']}"
                    if full_name == selected_owner:
                        customer_id = cust['customer_id']
                        break
                
                if not customer_id:
                    messagebox.showerror("Error", "Selected owner not found")
                    return
                
                age = int(age_var.get()) if age_var.get() else 1
                
                # weight validation for negative values
                weight = float(weight_entry.get()) if weight_entry.get() else 0
                if weight < 0:
                    messagebox.showerror("Error", "Weight cannot be negative")
                    return
                
                pet_data = {
                    'customer_id': customer_id,
                    'pet_name': pet_name_entry.get().strip(),
                    'pet_type': pet_type_var.get(),
                    'pet_age': age,
                    'breed': breed_entry.get().strip(),
                    'weight': weight
                }
                
                # create pet in db
                Pet.create(self.db, pet_data)
                messagebox.showinfo("Success", "Pet added successfully")
                dialog.destroy()  
                self.load_pets()  # refresh pet list
            except ValueError:
                # handle all errors
                messagebox.showerror("Error", "Please enter valid weight - number only")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add pet: {str(e)}")
        
        # cancel and add buttons
        tk.Button(buttons_frame, text="Cancel", command=dialog.destroy,
                 bg="#FF9800", fg="white", font=("Arial", 11),
                 padx=20, pady=8).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(buttons_frame, text="Add", command=save_pet,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 padx=20, pady=8).pack(side=tk.LEFT)
    
    def edit_pet(self, event):  # double-click for editing pet record
        selection = self.pet_tree.selection()
        if not selection:
            return  
        
        # get selected data
        item = self.pet_tree.item(selection[0])
        pet_id = item['values'][0]  
        
        # get pet details from db
        pets = Pet.get_all(self.db)
        pet = None
        for p in pets:
            if p['pet_id'] == pet_id:
                pet = p
                break
        
        if not pet:
            return  
        
        # create edit window
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Pet")
        dialog.geometry("400x350")
        
        customers = Customer.get_all(self.db)
        customer_list = [f"{c['customer_id']}: {c['first_name']} {c['last_name']}" for c in customers]
        
        current_customer = f"{pet['customer_id']}: {pet['first_name']} {pet['last_name']}"
        
        # customer dropdown
        tk.Label(dialog, text="Customer:", font=("Arial", 11)).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        customer_combo = ttk.Combobox(dialog, values=customer_list, state="readonly", width=27)
        customer_combo.set(current_customer)  
        customer_combo.grid(row=0, column=1, pady=10, padx=10)
        
        # pet name field
        tk.Label(dialog, text="Pet Name:", font=("Arial", 11)).grid(row=1, column=0, pady=10, padx=10, sticky="w")
        pet_name_entry = tk.Entry(dialog, width=30)
        pet_name_entry.insert(0, pet['pet_name'])  # pre-fill with existing data
        pet_name_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # pet type dropdown dog/cat
        tk.Label(dialog, text="Pet Type:", font=("Arial", 11)).grid(row=2, column=0, pady=10, padx=10, sticky="w")
        pet_type_var = tk.StringVar(value=pet['pet_type'])  
        pet_type_combo = ttk.Combobox(dialog, textvariable=pet_type_var, 
                                     values=["Dog", "Cat"], state="readonly", width=27)
        pet_type_combo.grid(row=2, column=1, pady=10, padx=10)
        
        # age dropdown from 1 to 16 y.o.
        tk.Label(dialog, text="Age:", font=("Arial", 11)).grid(row=3, column=0, pady=10, padx=10, sticky="w")
        age_values = [str(i) for i in range(1, 17)]  
    
        age_var = tk.StringVar(value=str(int(pet['pet_age'])) if pet['pet_age'] else "1")
        age_combo = ttk.Combobox(dialog, textvariable=age_var, 
                                values=age_values, state="readonly", width=27)
        age_combo.grid(row=3, column=1, pady=10, padx=10)
        
        # breed field
        tk.Label(dialog, text="Breed:", font=("Arial", 11)).grid(row=4, column=0, pady=10, padx=10, sticky="w")
        breed_entry = tk.Entry(dialog, width=30)
        breed_entry.insert(0, pet['breed'] or "")  
        breed_entry.grid(row=4, column=1, pady=10, padx=10)
        
        def update_pet():  # update pet record
            if not customer_combo.get():
                messagebox.showerror("Error", "Please select a customer")
                return
            
            if not pet_name_entry.get().strip():
                messagebox.showerror("Error", "Pet name is required")
                return
            
            try:
                customer_id = int(customer_combo.get().split(":")[0])
                age = int(age_var.get()) if age_var.get() else 1
                
                pet_data = {
                    'customer_id': customer_id,
                    'pet_name': pet_name_entry.get().strip(),
                    'pet_type': pet_type_var.get(),
                    'pet_age': age,
                    'breed': breed_entry.get().strip(),
                    'weight': pet.get('weight', 0)  
                }
                
                # update pet in db
                Pet.update(self.db, pet_id, pet_data)
                messagebox.showinfo("Success", "Pet updated successfully")
                dialog.destroy()  
                self.load_pets()  # refresh pet list
            except ValueError:
                # handle any errors
                messagebox.showerror("Error", "Please enter valid age (1-16)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update pet: {str(e)}")
        
        # update button
        tk.Button(dialog, text="Update", command=update_pet,
                 bg="#2196F3", fg="white", padx=20, pady=10).grid(row=5, column=0, columnspan=2, pady=20)

def main():  # to start app
    root = tk.Tk()  # create main window
    app = PetBoardingApp(root) 
    root.mainloop()  

if __name__ == "__main__":
    main()