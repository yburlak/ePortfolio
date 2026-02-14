# # SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Business logic and data handling
# 2026-01-31: Refactored to separate app logic from entry point
# 2026-02-07: Added authentication controllers and data validation

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re
from models.customer import Customer
from models.pet import Pet
from services.boarding_service import BoardingService
from services.checkout_service import CheckoutService
from services.report_service import ReportService
import services.auth_service

# validation functions:

def validate_name(name, field_name="Name"):# names contain only letters and spaces with minimum 2 characters
    
    if not name or not name.strip():
        return False, f"{field_name} cannot be empty"
    # check for letters only (no numbers or special characters)
    if not re.match(r"^[A-Za-z\s]+$", name):
        return False, f"{field_name} can only contain letters"
    
    # min=2
    if len(name.strip()) < 2:
        return False, f"{field_name} must be at least 2 characters"
    
    return True, ""

def validate_phone(phone):# phone numbers 10 digits with common separators allowed
    
    if not phone or not phone.strip():
        return False, "Phone number cannot be empty"
    
    # remove separators to check digit count
    clean_phone = re.sub(r'[\s\-\(\)\.]+', '', phone)
    
    # verify only digits remain after removing separators
    if not clean_phone.isdigit():
        return False, "Phone number can only contain digits and common separators"
    
    # min=10
    if len(clean_phone) != 10:
        return False, "Phone number must be 10 digits"
    
    return True, ""

def validate_email(email): # email format requiring @ and domain
    
    if not email or not email.strip():
        return False, "Email cannot be empty"
    
    # email format xxxx@xxxx.xxx
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email.strip()):
        return False, "Invalid email format. Must contain '@' and domain"
    
    return True, ""

def validate_weight(weight_str, pet_type=None): # weight is positive number under 200 lbs
    
    if not weight_str or not weight_str.strip():
        if pet_type and pet_type.lower() == "dog":
            return False, "Weight is required for dogs"
        return False, "Weight cannot be empty"
    
    try:
        weight = float(weight_str)
        if weight <= 0:
            return False, "Weight must be a positive number"
        if weight > 200:  # max=200
            return False, "Weight cannot exceed 200 lbs"
        return True, ""
    except ValueError:
        return False, "Weight must be a valid number"

def validate_pet_name(pet_name): # pet names with same rules as human names
    
    if not pet_name or not pet_name.strip():
        return False, "Pet name cannot be empty"
    
    if not re.match(r"^[A-Za-z\s]+$", pet_name):
        return False, "Pet name can only contain letters"
    
    if len(pet_name.strip()) < 2:
        return False, "Pet name must be at least 2 characters"
    
    return True, ""

def validate_breed(breed): # breed names with same rules as human names
    
    if not breed or not breed.strip():
        return False, "Breed cannot be empty"
    
    if not re.match(r"^[A-Za-z\s]+$", breed):
        return False, "Breed can only contain letters"
    
    if len(breed.strip()) < 2:
        return False, "Breed must be at least 2 characters"
    
    return True, ""

# main controllers class: all application logic
class AppControllers:
    def __init__(self, db, current_user):
        self.db = db  # database connection
        self.current_user = current_user  # currently logged in user
        self.views = None  
    
    def set_views(self, views):
        # connect controllers to UI components
        self.views = views
        self.load_customers()
        self.load_pets()
        self.update_dashboard()
    
    def get_available_spaces(self):
        # get current boarding capacity
        return BoardingService.get_available_spaces(self.db)
    
    def show_change_password(self):
        # open password change dialog
        ChangePasswordDialog(self.db, self.current_user['user_id']).show()
    
    def logout(self):
        # handle user logout
        response = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if response:
            result, message = services.auth_service.AuthService.logout_user()
            if result:
                messagebox.showinfo("Success", message)
                self.views.root.destroy()
    
    def load_customers(self):
        # populate customer tab with all customers
        if not self.views:
            return
            
        # clear existing entries
        for item in self.views.customer_tree.get_children():
            self.views.customer_tree.delete(item)
        
        try:
            customers = Customer.get_all(self.db)
            if customers:
                for cust in customers:
                    # Insert customer data into treeview
                    self.views.customer_tree.insert("", tk.END, values=(
                        cust['customer_id'],
                        cust['first_name'],
                        cust['last_name'],
                        cust['phone'] or "",
                        cust['email'] or ""
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")
    
    def load_pets(self):
        # populate pet tab with all pets
        if not self.views:
            return
            
        # clear existing entries
        for item in self.views.pet_tree.get_children():
            self.views.pet_tree.delete(item)
        
        try:
            pets = Pet.get_all(self.db)
            if pets:
                for pet in pets:
                    owner = f"{pet['first_name']} {pet['last_name']}"
                    # Insert pet data into treeview
                    self.views.pet_tree.insert("", tk.END, values=(
                        pet['pet_id'],
                        pet['pet_name'],
                        pet['pet_type'],
                        pet['pet_age'],
                        pet['breed'] or "",
                        owner
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load pets: {str(e)}")
    
    def show_checkin_form(self):
        # open check-in dialog for new bookings
        CheckinDialog(self.db, self).show()
    
    def show_checkout_form(self):
        # open checkout dialog
        CheckoutDialog(self.db, self).show()
    
    def add_customer(self):
        # open add customer dialog
        AddCustomerDialog(self.db, self).show()
    
    def edit_customer(self, event=None):
        # open edit dialog for selected customer
        selection = self.views.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to edit")
            return
        
        item = self.views.customer_tree.item(selection[0])
        customer_id = item['values'][0]
        EditCustomerDialog(self.db, customer_id, self).show()
    
    def delete_customer(self):
        # delete selected customer with cascading delete 
        selection = self.views.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to delete")
            return
        
        item = self.views.customer_tree.item(selection[0])
        customer_id = item['values'][0]
        customer_name = f"{item['values'][1]} {item['values'][2]}"
        
        # Warn about cascading deletion of related records
        response = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete customer '{customer_name}'?\n\n"
            f"This will also delete all their pets, boarding records, and grooming records!"
        )
        
        if response:
            try:
                success = Customer.delete_by_id(self.db, customer_id)
                if success:
                    messagebox.showinfo("Success", f"Customer '{customer_name}' deleted successfully")
                    self.load_customers()
                    self.load_pets()
                    self.update_dashboard()
                else:
                    messagebox.showerror("Error", "Failed to delete customer")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete customer: {str(e)}")
    
    def add_pet(self):
        # open add pet dialog
        AddPetDialog(self.db, self).show()
    
    def edit_pet(self, event=None):
        # open edit dialog for selected pet
        selection = self.views.pet_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a pet to edit")
            return
        
        item = self.views.pet_tree.item(selection[0])
        pet_id = item['values'][0]
        EditPetDialog(self.db, pet_id, self).show()
    
    def delete_pet(self):
        # delete selected pet with boarding status check
        selection = self.views.pet_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a pet to delete")
            return
        
        item = self.views.pet_tree.item(selection[0])
        pet_id = item['values'][0]
        pet_name = item['values'][1]
        owner_name = item['values'][5]
        
        # confirm deletion warning
        response = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete pet '{pet_name}' (Owner: {owner_name})?\n\n"
            f"This will also delete all boarding and grooming records for this pet!"
        )
        
        if response:
            try:
                # Check if pet is currently boarded
                cursor = self.db.connection.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM Boarding 
                    WHERE pet_id = %s AND check_out IS NULL
                """, (pet_id,))
                is_boarding = cursor.fetchone()[0] > 0
                cursor.close()
                
                # additional warning if pet is currently boarded
                if is_boarding:
                    response2 = messagebox.askyesno(
                        "Pet is Currently Boarded",
                        f"Pet '{pet_name}' is currently boarded!\n\n"
                        f"If you delete this pet, the boarding space will be freed up.\n"
                        f"Continue with deletion?"
                    )
                    if not response2:
                        return
                
                success = Pet.delete_by_id(self.db, pet_id)
                if success:
                    messagebox.showinfo("Success", f"Pet '{pet_name}' deleted successfully")
                    self.load_pets()
                    self.update_dashboard()
                else:
                    messagebox.showerror("Error", "Failed to delete pet")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete pet: {str(e)}")
    
    def update_dashboard(self):
        # update dashboard display with current boarding capacity
        spaces = BoardingService.get_available_spaces(self.db)
        if self.views:
            self.views.dog_spaces_label.config(text=f"Available: {spaces['dog_spaces']} of 30")
            self.views.cat_spaces_label.config(text=f"Available: {spaces['cat_spaces']} of 12")
    
    def generate_occupancy_report(self, period_days):
        # generate occupancy report
        try:
            report = ReportService.get_occupancy_report(self.db, period_days)
            self.views.display_report(report)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate occupancy report: {str(e)}")
    
    def generate_revenue_report(self, period_days):
        # generate revenue report
        try:
            report = ReportService.get_revenue_report(self.db, period_days)
            self.views.display_report(report)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate revenue report: {str(e)}")

# dialog classes
class CheckinDialog:
    def __init__(self, db, controller):
        self.db = db
        self.controller = controller
        
    def show(self):
        # create and display check-in dialog window
        dialog = tk.Toplevel()
        dialog.title("New Booking - Check-In")
        dialog.geometry("600x400")
        dialog.resizable(False, False)
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side form fields
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        tk.Label(left_frame, text="Owner:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        owner_entry = tk.Entry(left_frame, width=28)
        owner_entry.pack(anchor="w", pady=(0, 15))
        
        tk.Label(left_frame, text="Pet Type:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        pet_type_var = tk.StringVar(value="Dog")
        pet_type_combo = ttk.Combobox(left_frame, textvariable=pet_type_var, 
                                     values=["Dog", "Cat"], state="readonly", width=25)
        pet_type_combo.pack(anchor="w", pady=(0, 15))
        
        tk.Label(left_frame, text="Pet Name:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        pet_name_entry = tk.Entry(left_frame, width=28)
        pet_name_entry.pack(anchor="w", pady=(0, 15))
        
        grooming_var = tk.BooleanVar()
        tk.Checkbutton(left_frame, text="Grooming Requested", 
                      variable=grooming_var, font=("Arial", 11)).pack(anchor="w", pady=15)
        
        # right side form fields
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="Breed:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        breed_entry = tk.Entry(right_frame, width=28)
        breed_entry.pack(anchor="w", pady=(0, 15))
        
        tk.Label(right_frame, text="Age:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        age_values = [str(i) for i in range(1, 17)]
        age_var = tk.StringVar(value="1")
        age_combo = ttk.Combobox(right_frame, textvariable=age_var, 
                                values=age_values, state="readonly", width=25)
        age_combo.pack(anchor="w", pady=(0, 15))
        
        tk.Label(right_frame, text="Weight:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        weight_frame = tk.Frame(right_frame)
        weight_frame.pack(anchor="w", pady=(0, 15))
        
        weight_entry = tk.Entry(weight_frame, width=10)
        weight_entry.pack(side=tk.LEFT)
        tk.Label(weight_frame, text=" lbs").pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Label(right_frame, text="Days Stay:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        days_values = [str(i) for i in range(1, 32)]
        days_var = tk.StringVar(value="1")
        days_combo = ttk.Combobox(right_frame, textvariable=days_var, 
                                 values=days_values, state="readonly", width=25)
        days_combo.pack(anchor="w", pady=(0, 15))
        
        # action buttons
        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def check_in():
            # validate all input fields before completing check-in
            pet_name = pet_name_entry.get().strip()
            is_valid, error = validate_pet_name(pet_name)
            if not is_valid:
                messagebox.showerror("Error", error)
                return
            
            owner_name = owner_entry.get().strip()
            is_valid, error = validate_name(owner_name, "Owner name")
            if not is_valid:
                messagebox.showerror("Error", error)
                return
            
            breed = breed_entry.get().strip()
            is_valid, error = validate_breed(breed)
            if not is_valid:
                messagebox.showerror("Error", error)
                return
            
            try:
                pet_type = pet_type_var.get()
                age = int(age_var.get())
                days_stay = int(days_var.get())
                
                # validate age range
                if age <= 0 or age > 30:
                    messagebox.showerror("Error", "Age must be between 1 and 30 years")
                    return
                
                # validate stay duration
                if days_stay <= 0 or days_stay > 365:
                    messagebox.showerror("Error", "Days stay must be between 1 and 365")
                    return
                
                # validate weight based on pet type
                weight_str = weight_entry.get() if weight_entry.get() else "0"
                is_valid, error = validate_weight(weight_str, pet_type)
                if not is_valid:
                    messagebox.showerror("Validation Error", error)
                    return
                
                weight = float(weight_str)
                grooming = grooming_var.get()
                
                # find or create customer
                customers = Customer.get_all(self.db)
                customer_exists = False
                customer_id = None
                
                for cust in customers:
                    full_name = f"{cust['first_name']} {cust['last_name']}"
                    if owner_name.lower() in full_name.lower():
                        customer_exists = True
                        customer_id = cust['customer_id']
                        break
                
                # create new customer if not found
                if not customer_exists:
                    name_parts = owner_name.split()
                    first_name = name_parts[0] if len(name_parts) > 0 else owner_name
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
                    
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
                
                # process boarding check-in
                success, message = BoardingService.check_in_pet(
                    self.db, pet_id, days_stay, grooming
                )
                
                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                    # Refresh UI components
                    self.controller.load_pets()
                    self.controller.load_customers()
                    self.controller.update_dashboard()
                else:
                    messagebox.showerror("Error", message)
                    
            except ValueError as e:
                messagebox.showerror("Error", f"Please enter valid data: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        # add buttons to dialog
        tk.Button(buttons_frame, text="Check-In", command=check_in,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 padx=30, pady=10).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(buttons_frame, text="Cancel", command=dialog.destroy,
                 bg="#FF9800", fg="white", font=("Arial", 11),
                 padx=30, pady=10).pack(side=tk.RIGHT)
        
        # make dialog
        dialog.grab_set()
        dialog.wait_window()

class CheckoutDialog:
    def __init__(self, db, controller):
        self.db = db
        self.controller = controller
        
    def show(self):
        # create checkout dialog
        dialog = tk.Toplevel()
        dialog.title("Check-Out")
        dialog.geometry("500x550")
        dialog.resizable(False, False)
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Select Pet:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))
        
        # get currently boarded pets
        boardings = BoardingService.get_current_boardings(self.db)
        boarding_list = [f"{b['pet_name']} (Owner: {b['first_name']} {b['last_name']})" for b in boardings]
        
        pet_var = tk.StringVar()
        pet_combo = ttk.Combobox(main_frame, textvariable=pet_var, 
                                values=boarding_list, state="readonly", width=40)
        pet_combo.pack(anchor="w", pady=(0, 20))
        
        # pet details display frame
        details_frame = tk.LabelFrame(main_frame, text="Pet Details", padx=10, pady=10)
        details_frame.pack(fill=tk.X, pady=(0, 20))
        
        pet_name_label = tk.Label(details_frame, text="Pet Name: ", anchor="w")
        pet_name_label.pack(fill=tk.X, pady=2)
        
        owner_label = tk.Label(details_frame, text="Owner: ", anchor="w")
        owner_label.pack(fill=tk.X, pady=2)
        
        days_label = tk.Label(details_frame, text="Boarding Days: ", anchor="w")
        days_label.pack(fill=tk.X, pady=2)
        
        weight_label = tk.Label(details_frame, text="Weight: ", anchor="w")
        weight_label.pack(fill=tk.X, pady=2)
        
        grooming_label = tk.Label(details_frame, text="Grooming: ", anchor="w")
        grooming_label.pack(fill=tk.X, pady=2)
        
        # payment information frame
        amount_frame = tk.LabelFrame(main_frame, text="Payment", padx=10, pady=10)
        amount_frame.pack(fill=tk.X, pady=(0, 20))
        
        amount_label = tk.Label(amount_frame, text="Total Amount Due: $0.00", 
                                font=("Arial", 12, "bold"))
        amount_label.pack(anchor="w")
        
        # action buttons frame
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        def calculate_total():
            # calculate and display total amount due for selected pet
            selection = pet_combo.get()
            if selection and boardings:
                for b in boardings:
                    display_name = f"{b['pet_name']} (Owner: {b['first_name']} {b['last_name']})"
                    if display_name == selection:
                        # get grooming price if applicable
                        cursor = self.db.connection.cursor(dictionary=True)
                        cursor.execute("""
                            SELECT price FROM Grooming 
                            WHERE boarding_id = %s
                        """, (b['boarding_id'],))
                        grooming = cursor.fetchone()
                        cursor.close()
                        
                        grooming_price = grooming['price'] if grooming else 0
                        total = b['amount_due']
                        
                        amount_label.config(text=f"Total Amount Due: ${total:.2f}")
                        
                        # update detail labels
                        pet_name_label.config(text=f"Pet Name: {b['pet_name']}")
                        owner_label.config(text=f"Owner: {b['first_name']} {b['last_name']}")
                        days_label.config(text=f"Boarding Days: {b['days_stay']}")
                        weight_label.config(text=f"Weight: {b.get('weight', 0)} lbs")
                        
                        # format grooming information with tier pricing for dogs
                        if b['pet_type'].lower() == 'dog' and b.get('weight', 0):
                            grooming_tier = ""
                            for tier, details in BoardingService.GROOMING_PRICES.items():
                                if details['min'] <= b['weight'] <= details['max']:
                                    grooming_tier = f" ({tier.title()} - ${details['price']})"
                                    break
                            grooming_text = f"Grooming: {'Yes' + grooming_tier if b['grooming_requested'] else 'No'}"
                        else:
                            grooming_text = f"Grooming: {'Yes' if b['grooming_requested'] else 'No'}"
                        grooming_label.config(text=grooming_text)
                        break
        
        def confirm_checkout():
            # process checkout for selected pet
            selection = pet_combo.get()
            if not selection:
                messagebox.showerror("Error", "Please select a pet")
                return
            
            response = messagebox.askyesno("Confirm Check-out", 
                                          f"Check out {selection.split('(')[0].strip()}?")
            if response:
                for b in boardings:
                    display_name = f"{b['pet_name']} (Owner: {b['first_name']} {b['last_name']})"
                    if display_name == selection:
                        success, message, amount = CheckoutService.check_out_pet(self.db, b['boarding_id'])
                        if success:
                            dialog.destroy()
                            
                            # Generate and display invoice
                            invoice = CheckoutService.generate_invoice(self.db, b['boarding_id'])
                            if invoice:
                                invoice_dialog = tk.Toplevel()
                                invoice_dialog.title("Invoice")
                                invoice_dialog.geometry("400x500")
                                
                                text_widget = tk.Text(invoice_dialog, wrap=tk.WORD)
                                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                                text_widget.insert(1.0, invoice)
                                text_widget.config(state=tk.DISABLED)
                            
                            messagebox.showinfo("Success", message)
                            self.controller.update_dashboard()
                        else:
                            messagebox.showerror("Error", message)
                        break
        
        def generate_invoice():
            # generate invoice without checking out
            selection = pet_combo.get()
            if not selection:
                messagebox.showerror("Error", "Please select a pet")
                return
            
            for b in boardings:
                display_name = f"{b['pet_name']} (Owner: {b['first_name']} {b['last_name']})"
                if display_name == selection:
                    invoice = CheckoutService.generate_invoice(self.db, b['boarding_id'])
                    if invoice:
                        invoice_dialog = tk.Toplevel(dialog)
                        invoice_dialog.title("Invoice")
                        invoice_dialog.geometry("400x500")
                        
                        text_widget = tk.Text(invoice_dialog, wrap=tk.WORD)
                        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                        text_widget.insert(1.0, invoice)
                        text_widget.config(state=tk.DISABLED)
                    break
        
        # add action buttons
        tk.Button(buttons_frame, text="Calculate Total", command=calculate_total,
                 bg="#2196F3", fg="white", font=("Arial", 10),
                 padx=15, pady=8).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(buttons_frame, text="Confirm Check-out", command=confirm_checkout,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons_frame, text="Invoice", command=generate_invoice,
                 bg="#2196F3", fg="white", font=("Arial", 10),
                 padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons_frame, text="Cancel", command=dialog.destroy,
                 bg="#FF9800", fg="white", font=("Arial", 10),
                 padx=15, pady=8).pack(side=tk.RIGHT)
        
        # Make dialog modal
        dialog.grab_set()
        dialog.wait_window()

class AddCustomerDialog:
    def __init__(self, db, controller):
        self.db = db
        self.controller = controller
        
    def show(self):
        # create add customer dialog
        dialog = tk.Toplevel()
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
        
        def save_customer():
            # validate and save new customer
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            
            # validate first name
            is_valid, error = validate_name(first_name, "First name")
            if not is_valid:
                messagebox.showerror("Validation Error", error)
                return
            
            # validate last name
            is_valid, error = validate_name(last_name, "Last name")
            if not is_valid:
                messagebox.showerror("Validation Error", error)
                return
            
            # validate phone
            is_valid, error = validate_phone(phone)
            if not is_valid:
                messagebox.showerror("Validation Error", error)
                return
            
            # validate email
            is_valid, error = validate_email(email)
            if not is_valid:
                messagebox.showerror("Validation Error", error)
                return
            
            customer_data = {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'email': email
            }
            
            try:
                Customer.create(self.db, customer_data)
                messagebox.showinfo("Success", "Customer added successfully")
                dialog.destroy()
                self.controller.load_customers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add customer: {str(e)}")
        
        tk.Button(dialog, text="Save", command=save_customer,
                 bg="#2196F3", fg="white", padx=20, pady=10).grid(row=4, column=0, columnspan=2, pady=20)
        
        dialog.grab_set()
        dialog.wait_window()

class EditCustomerDialog:
    def __init__(self, db, customer_id, controller):
        self.db = db
        self.customer_id = customer_id
        self.controller = controller
        
    def show(self):
        # load customer data for editing
        customers = Customer.get_all(self.db)
        customer = None
        for cust in customers:
            if cust['customer_id'] == self.customer_id:
                customer = cust
                break
        
        if not customer:
            return
        
        # create edit customer dialog
        dialog = tk.Toplevel()
        dialog.title("Edit Customer")
        dialog.geometry("400x300")
        
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
        
        def update_customer():
            # validate and update customer information
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            
            # validate first name
            is_valid, error = validate_name(first_name, "First name")
            if not is_valid:
                messagebox.showerror("Validation Error", error)
                return
            
            # validate last name
            is_valid, error = validate_name(last_name, "Last name")
            if not is_valid:
                messagebox.showerror("Validation Error", error)
                return
            
            # validate phone
            is_valid, error = validate_phone(phone)
            if not is_valid:
                messagebox.showerror("Validation Error", error)
                return
            
            # validate email
            is_valid, error = validate_email(email)
            if not is_valid:
                messagebox.showerror("Validation Error", error)
                return
            
            customer_data = {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'email': email
            }
            
            try:
                Customer.update(self.db, self.customer_id, customer_data)
                messagebox.showinfo("Success", "Customer updated successfully")
                dialog.destroy()
                self.controller.load_customers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update customer: {str(e)}")
        
        tk.Button(dialog, text="Update", command=update_customer,
                 bg="#2196F3", fg="white", padx=20, pady=10).grid(row=4, column=0, columnspan=2, pady=20)
        
        dialog.grab_set()
        dialog.wait_window()

class AddPetDialog:
    def __init__(self, db, controller):
        self.db = db
        self.controller = controller
        
    def show(self):
        # create add pet dialog
        dialog = tk.Toplevel()
        dialog.title("Add Pet")
        dialog.geometry("400x400")
        
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content_frame, text="Owner:", font=("Arial", 11)).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        
        # populate owner dropdown
        customers = Customer.get_all(self.db)
        customer_list = [f"{c['first_name']} {c['last_name']}" for c in customers]
        
        owner_combo = ttk.Combobox(content_frame, values=customer_list, state="readonly", width=25)
        owner_combo.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(content_frame, text="Pet Type:", font=("Arial", 11)).grid(row=1, column=0, pady=10, padx=10, sticky="w")
        pet_type_var = tk.StringVar(value="Dog")
        pet_type_combo = ttk.Combobox(content_frame, textvariable=pet_type_var, 
                                     values=["Dog", "Cat"], state="readonly", width=25)
        pet_type_combo.grid(row=1, column=1, pady=10, padx=10)
        
        tk.Label(content_frame, text="Pet Name:", font=("Arial", 11)).grid(row=2, column=0, pady=10, padx=10, sticky="w")
        pet_name_entry = tk.Entry(content_frame, width=28)
        pet_name_entry.grid(row=2, column=1, pady=10, padx=10)
        
        tk.Label(content_frame, text="Breed:", font=("Arial", 11)).grid(row=3, column=0, pady=10, padx=10, sticky="w")
        breed_entry = tk.Entry(content_frame, width=28)
        breed_entry.grid(row=3, column=1, pady=10, padx=10)
        
        tk.Label(content_frame, text="Age:", font=("Arial", 11)).grid(row=4, column=0, pady=10, padx=10, sticky="w")
        age_values = [str(i) for i in range(1, 17)]
        age_var = tk.StringVar(value="1")
        age_combo = ttk.Combobox(content_frame, textvariable=age_var, 
                                values=age_values, state="readonly", width=25)
        age_combo.grid(row=4, column=1, pady=10, padx=10)
        
        tk.Label(content_frame, text="Weight:", font=("Arial", 11)).grid(row=5, column=0, pady=10, padx=10, sticky="w")
        weight_entry = tk.Entry(content_frame, width=28)
        weight_entry.grid(row=5, column=1, pady=10, padx=10)
        
        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def save_pet():
            # validate and save new pet
            if not owner_combo.get():
                messagebox.showerror("Error", "Please select an owner")
                return
            
            # validate pet name
            pet_name = pet_name_entry.get().strip()
            is_valid, error = validate_pet_name(pet_name)
            if not is_valid:
                messagebox.showerror("Error", error)
                return
            
            # validate breed
            breed = breed_entry.get().strip()
            is_valid, error = validate_breed(breed)
            if not is_valid:
                messagebox.showerror("Error", error)
                return
            
            try:
                # find selected customer ID
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
                
                # validate age
                age = int(age_var.get()) if age_var.get() else 1
                if age <= 0 or age > 30:
                    messagebox.showerror("Error", "Age must be between 1 and 30 years")
                    return
                
                pet_type = pet_type_var.get()
                
                # validate weight
                weight_str = weight_entry.get().strip()
                is_valid, error = validate_weight(weight_str, pet_type)
                if not is_valid:
                    messagebox.showerror("Validation Error", error)
                    return
                
                weight = float(weight_str)
                
                # create pet record
                pet_data = {
                    'customer_id': customer_id,
                    'pet_name': pet_name,
                    'pet_type': pet_type,
                    'pet_age': age,
                    'breed': breed,
                    'weight': weight
                }
                
                Pet.create(self.db, pet_data)
                messagebox.showinfo("Success", "Pet added successfully")
                dialog.destroy()
                self.controller.load_pets()
            except ValueError as e:
                if "Age must be" not in str(e):
                    messagebox.showerror("Error", "Please enter valid numeric values")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add pet: {str(e)}")
        
        # add action buttons
        tk.Button(buttons_frame, text="Cancel", command=dialog.destroy,
                 bg="#FF9800", fg="white", font=("Arial", 11),
                 padx=20, pady=8).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(buttons_frame, text="Add", command=save_pet,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 padx=20, pady=8).pack(side=tk.LEFT)
        
        dialog.grab_set()
        dialog.wait_window()

class EditPetDialog:
    def __init__(self, db, pet_id, controller):
        self.db = db
        self.pet_id = pet_id
        self.controller = controller
        
    def show(self):
        # load pet data for editing
        pets = Pet.get_all(self.db)
        pet = None
        for p in pets:
            if p['pet_id'] == self.pet_id:
                pet = p
                break
        
        if not pet:
            return
        
        # create edit pet dialog
        dialog = tk.Toplevel()
        dialog.title("Edit Pet")
        dialog.geometry("400x350")
        
        # prepare customer list for dropdown
        customers = Customer.get_all(self.db)
        customer_list = [f"{c['customer_id']}: {c['first_name']} {c['last_name']}" for c in customers]
        
        current_customer = f"{pet['customer_id']}: {pet['first_name']} {pet['last_name']}"
        
        tk.Label(dialog, text="Customer:", font=("Arial", 11)).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        customer_combo = ttk.Combobox(dialog, values=customer_list, state="readonly", width=27)
        customer_combo.set(current_customer)
        customer_combo.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(dialog, text="Pet Name:", font=("Arial", 11)).grid(row=1, column=0, pady=10, padx=10, sticky="w")
        pet_name_entry = tk.Entry(dialog, width=30)
        pet_name_entry.insert(0, pet['pet_name'])
        pet_name_entry.grid(row=1, column=1, pady=10, padx=10)
        
        tk.Label(dialog, text="Pet Type:", font=("Arial", 11)).grid(row=2, column=0, pady=10, padx=10, sticky="w")
        pet_type_var = tk.StringVar(value=pet['pet_type'])
        pet_type_combo = ttk.Combobox(dialog, textvariable=pet_type_var, 
                                     values=["Dog", "Cat"], state="readonly", width=27)
        pet_type_combo.grid(row=2, column=1, pady=10, padx=10)
        
        tk.Label(dialog, text="Age:", font=("Arial", 11)).grid(row=3, column=0, pady=10, padx=10, sticky="w")
        age_values = [str(i) for i in range(1, 17)]
        age_var = tk.StringVar(value=str(int(pet['pet_age'])) if pet['pet_age'] else "1")
        age_combo = ttk.Combobox(dialog, textvariable=age_var, 
                                values=age_values, state="readonly", width=27)
        age_combo.grid(row=3, column=1, pady=10, padx=10)
        
        tk.Label(dialog, text="Breed:", font=("Arial", 11)).grid(row=4, column=0, pady=10, padx=10, sticky="w")
        breed_entry = tk.Entry(dialog, width=30)
        breed_entry.insert(0, pet['breed'] or "")
        breed_entry.grid(row=4, column=1, pady=10, padx=10)
        
        def update_pet():
            # validate and update pet information
            if not customer_combo.get():
                messagebox.showerror("Error", "Please select a customer")
                return
            
            # validate pet name
            pet_name = pet_name_entry.get().strip()
            is_valid, error = validate_pet_name(pet_name)
            if not is_valid:
                messagebox.showerror("Error", error)
                return
            
            # validate breed
            breed = breed_entry.get().strip()
            is_valid, error = validate_breed(breed)
            if not is_valid:
                messagebox.showerror("Error", error)
                return
            
            try:
                customer_id = int(customer_combo.get().split(":")[0])
                age = int(age_var.get()) if age_var.get() else 1
                
                if age <= 0 or age > 30:
                    messagebox.showerror("Error", "Age must be between 1 and 30 years")
                    return
                
                # prepare updated pet data
                pet_data = {
                    'customer_id': customer_id,
                    'pet_name': pet_name,
                    'pet_type': pet_type_var.get(),
                    'pet_age': age,
                    'breed': breed,
                    'weight': pet.get('weight', 0)
                }
                
                Pet.update(self.db, self.pet_id, pet_data)
                messagebox.showinfo("Success", "Pet updated successfully")
                dialog.destroy()
                self.controller.load_pets()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid age (1-30)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update pet: {str(e)}")
        
        tk.Button(dialog, text="Update", command=update_pet,
                 bg="#2196F3", fg="white", padx=20, pady=10).grid(row=5, column=0, columnspan=2, pady=20)
        
        dialog.grab_set()
        dialog.wait_window()

class ChangePasswordDialog:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
        
    def show(self):
        # create password change dialog
        dialog = tk.Toplevel()
        dialog.title("Change Password")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Current Password:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        current_password_var = tk.StringVar()
        current_password_entry = tk.Entry(main_frame, textvariable=current_password_var, 
                                         show="*", width=30)
        current_password_entry.pack(anchor="w", pady=(0, 15))
        
        tk.Label(main_frame, text="New Password:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        new_password_var = tk.StringVar()
        new_password_entry = tk.Entry(main_frame, textvariable=new_password_var, 
                                     show="*", width=30)
        new_password_entry.pack(anchor="w", pady=(0, 15))
        
        tk.Label(main_frame, text="Confirm New Password:", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))
        confirm_password_var = tk.StringVar()
        confirm_password_entry = tk.Entry(main_frame, textvariable=confirm_password_var, 
                                         show="*", width=30)
        confirm_password_entry.pack(anchor="w", pady=(0, 25))
        
        requirements_label = tk.Label(main_frame, 
                                     text="Password must be at least 6 characters",
                                     font=("Arial", 9), fg="gray")
        requirements_label.pack(anchor="w", pady=(0, 20))
        
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        def change_password():
            # process password change request
            current = current_password_var.get()
            new = new_password_var.get()
            confirm = confirm_password_var.get()
            
            success, message = services.auth_service.AuthService.change_password(self.db, self.user_id, 
                                                          current, new, confirm)
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
            else:
                messagebox.showerror("Error", message)
        
        # add action buttons
        tk.Button(buttons_frame, text="Cancel", command=dialog.destroy,
                 bg="#FF9800", fg="white", padx=20, pady=8).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(buttons_frame, text="Change Password", command=change_password,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 padx=20, pady=8).pack(side=tk.LEFT)
        
        dialog.bind('<Return>', lambda e: change_password())
        dialog.wait_window()