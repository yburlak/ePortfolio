# # SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Business logic and data handling
# 2026-01-31: Refactored to separate app logic from entry point

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.customer import Customer
from models.pet import Pet
from services.boarding_service import BoardingService
from services.checkout_service import CheckoutService
from services.report_service import ReportService

class AppControllers:
    def __init__(self, db):
        self.db = db
        self.views = None
    
   # set the view reference from main
    def set_views(self, views):
        
        self.views = views
        self.load_customers()
        self.load_pets()
        self.update_dashboard()
    
    def get_available_spaces(self):
        return BoardingService.get_available_spaces(self.db)
    
    def load_customers(self):
        if not self.views:
            return
            
        for item in self.views.customer_tree.get_children():
            self.views.customer_tree.delete(item)
        
        try:
            customers = Customer.get_all(self.db)
            if customers:
                for cust in customers:
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
        if not self.views:
            return
            
        for item in self.views.pet_tree.get_children():
            self.views.pet_tree.delete(item)
        
        try:
            pets = Pet.get_all(self.db)
            if pets:
                for pet in pets:
                    owner = f"{pet['first_name']} {pet['last_name']}"
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
        CheckinDialog(self.db, self).show()
    
    def show_checkout_form(self):
        CheckoutDialog(self.db, self).show()
    
    def add_customer(self):
        AddCustomerDialog(self.db, self).show()
    
    def edit_customer(self, event=None):
        selection = self.views.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to edit")
            return
        
        item = self.views.customer_tree.item(selection[0])
        customer_id = item['values'][0]
        EditCustomerDialog(self.db, customer_id, self).show()
    
    def delete_customer(self):
        selection = self.views.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer to delete")
            return
        
        item = self.views.customer_tree.item(selection[0])
        customer_id = item['values'][0]
        customer_name = f"{item['values'][1]} {item['values'][2]}"
        
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
        AddPetDialog(self.db, self).show()
    
    def edit_pet(self, event=None):
        selection = self.views.pet_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a pet to edit")
            return
        
        item = self.views.pet_tree.item(selection[0])
        pet_id = item['values'][0]
        EditPetDialog(self.db, pet_id, self).show()
    
    def delete_pet(self):
        selection = self.views.pet_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a pet to delete")
            return
        
        item = self.views.pet_tree.item(selection[0])
        pet_id = item['values'][0]
        pet_name = item['values'][1]
        owner_name = item['values'][5]
        
        response = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete pet '{pet_name}' (Owner: {owner_name})?\n\n"
            f"This will also delete all boarding and grooming records for this pet!"
        )
        
        if response:
            try:
                cursor = self.db.connection.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM Boarding 
                    WHERE pet_id = %s AND check_out IS NULL
                """, (pet_id,))
                is_boarding = cursor.fetchone()[0] > 0
                cursor.close()
                
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
        spaces = BoardingService.get_available_spaces(self.db)
        if self.views:
            self.views.dog_spaces_label.config(text=f"Available: {spaces['dog_spaces']} of 30")
            self.views.cat_spaces_label.config(text=f"Available: {spaces['cat_spaces']} of 12")
    
    def generate_occupancy_report(self, period_days):
        try:
            report = ReportService.get_occupancy_report(self.db, period_days)
            self.views.display_report(report)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate occupancy report: {str(e)}")
    
    def generate_revenue_report(self, period_days):
        try:
            report = ReportService.get_revenue_report(self.db, period_days)
            self.views.display_report(report)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate revenue report: {str(e)}")


class CheckinDialog:
    def __init__(self, db, controller):
        self.db = db
        self.controller = controller
        
    def show(self):
        dialog = tk.Toplevel()
        dialog.title("New Booking - Check-In")
        dialog.geometry("600x400")
        dialog.resizable(False, False)
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
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
        
        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def check_in():
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
                weight = float(weight_entry.get()) if weight_entry.get() else 0
                grooming = grooming_var.get()
                
                customers = Customer.get_all(self.db)
                customer_exists = False
                customer_id = None
                
                for cust in customers:
                    full_name = f"{cust['first_name']} {cust['last_name']}"
                    if owner_name.lower() in full_name.lower():
                        customer_exists = True
                        customer_id = cust['customer_id']
                        break
                
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
                
                pet_data = {
                    'customer_id': customer_id,
                    'pet_name': pet_name,
                    'pet_type': pet_type,
                    'pet_age': age,
                    'breed': breed,
                    'weight': weight
                }
                pet_id = Pet.create(self.db, pet_data)
                
                success, message = BoardingService.check_in_pet(
                    self.db, pet_id, days_stay, grooming
                )
                
                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                    self.controller.load_pets()
                    self.controller.load_customers()
                    self.controller.update_dashboard()
                else:
                    messagebox.showerror("Error", message)
                    
            except ValueError as e:
                messagebox.showerror("Error", f"Please enter valid data: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        tk.Button(buttons_frame, text="Check-In", command=check_in,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"),
                 padx=30, pady=10).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(buttons_frame, text="Cancel", command=dialog.destroy,
                 bg="#FF9800", fg="white", font=("Arial", 11),
                 padx=30, pady=10).pack(side=tk.RIGHT)
        
        dialog.grab_set()
        dialog.wait_window()


class CheckoutDialog:
    def __init__(self, db, controller):
        self.db = db
        self.controller = controller
        
    def show(self):
        dialog = tk.Toplevel()
        dialog.title("Check-Out")
        dialog.geometry("500x550")
        dialog.resizable(False, False)
        
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Select Pet:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))
        
        boardings = BoardingService.get_current_boardings(self.db)
        boarding_list = [f"{b['pet_name']} (Owner: {b['first_name']} {b['last_name']})" for b in boardings]
        
        pet_var = tk.StringVar()
        pet_combo = ttk.Combobox(main_frame, textvariable=pet_var, 
                                values=boarding_list, state="readonly", width=40)
        pet_combo.pack(anchor="w", pady=(0, 20))
        
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
        
        amount_frame = tk.LabelFrame(main_frame, text="Payment", padx=10, pady=10)
        amount_frame.pack(fill=tk.X, pady=(0, 20))
        
        amount_label = tk.Label(amount_frame, text="Total Amount Due: $0.00", 
                                font=("Arial", 12, "bold"))
        amount_label.pack(anchor="w")
        
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        def calculate_total():
            selection = pet_combo.get()
            if selection and boardings:
                for b in boardings:
                    display_name = f"{b['pet_name']} (Owner: {b['first_name']} {b['last_name']})"
                    if display_name == selection:
                        # Get grooming price
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
                        
                        pet_name_label.config(text=f"Pet Name: {b['pet_name']}")
                        owner_label.config(text=f"Owner: {b['first_name']} {b['last_name']}")
                        days_label.config(text=f"Boarding Days: {b['days_stay']}")
                        weight_label.config(text=f"Weight: {b.get('weight', 0)} lbs")
                        
                        if b['pet_type'].lower() == 'dog' and b.get('weight', 0):
                            # Determine grooming tier
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
        
        dialog.grab_set()
        dialog.wait_window()


class AddCustomerDialog:
    def __init__(self, db, controller):
        self.db = db
        self.controller = controller
        
    def show(self):
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
        customers = Customer.get_all(self.db)
        customer = None
        for cust in customers:
            if cust['customer_id'] == self.customer_id:
                customer = cust
                break
        
        if not customer:
            return
        
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
        dialog = tk.Toplevel()
        dialog.title("Add Pet")
        dialog.geometry("400x400")
        
        content_frame = tk.Frame(dialog, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content_frame, text="Owner:", font=("Arial", 11)).grid(row=0, column=0, pady=10, padx=10, sticky="w")
        
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
                
                Pet.create(self.db, pet_data)
                messagebox.showinfo("Success", "Pet added successfully")
                dialog.destroy()
                self.controller.load_pets()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid weight - number only")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add pet: {str(e)}")
        
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
        pets = Pet.get_all(self.db)
        pet = None
        for p in pets:
            if p['pet_id'] == self.pet_id:
                pet = p
                break
        
        if not pet:
            return
        
        dialog = tk.Toplevel()
        dialog.title("Edit Pet")
        dialog.geometry("400x350")
        
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
                
                Pet.update(self.db, self.pet_id, pet_data)
                messagebox.showinfo("Success", "Pet updated successfully")
                dialog.destroy()
                self.controller.load_pets()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid age (1-16)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update pet: {str(e)}")
        
        tk.Button(dialog, text="Update", command=update_pet,
                 bg="#2196F3", fg="white", padx=20, pady=10).grid(row=5, column=0, columnspan=2, pady=20)
        
        dialog.grab_set()
        dialog.wait_window()