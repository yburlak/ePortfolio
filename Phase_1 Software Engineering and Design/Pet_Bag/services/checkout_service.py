# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: CheckoutService handles check-out operations for pets and generates invoice 

from models.pet import Pet
from datetime import date

class CheckoutService:
    
    @staticmethod
    def check_out_pet(db, boarding_id):

        try:
            # get boarding record
            cursor = db.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT b.*, p.pet_id, p.pet_name, p.pet_type
                FROM Boarding b
                JOIN Pet p ON b.pet_id = p.pet_id
                WHERE b.boarding_id = %s
            """, (boarding_id,))
            boarding = cursor.fetchone()
            
            if not boarding:
                return False, "Boarding record not found", 0
            
            # update boarding record with check-out date
            cursor.execute("""
                UPDATE Boarding 
                SET check_out = %s 
                WHERE boarding_id = %s
            """, (date.today(), boarding_id))
            
            # return space to availability
            if boarding['pet_type'] == "dog":
                Pet.dog_spaces += 1
            elif boarding['pet_type'] == "cat":
                Pet.cat_spaces += 1
            
            db.connection.commit()
            cursor.close()
            
            message = f"{boarding['pet_name']} checked out successfully.\n"
            message += f"Amount paid: ${boarding['amount_due']:.2f}"
            
            return True, message, boarding['amount_due']
            
        except Exception as e:
            return False, f"Check-out failed: {str(e)}", 0
    
    @staticmethod
    def generate_invoice(db, boarding_id):

        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, p.pet_name, p.pet_type, p.breed,
                   c.first_name, c.last_name, c.phone, c.email
            FROM Boarding b
            JOIN Pet p ON b.pet_id = p.pet_id
            JOIN Customer c ON p.customer_id = c.customer_id
            WHERE b.boarding_id = %s
        """, (boarding_id,))
        
        boarding = cursor.fetchone()
        cursor.close()
        
        if not boarding:
            return None
        
        # create invoice text
        invoice = f"""
INVOICE #BOARD{boarding_id:04d}
Date: {date.today()}

Customer: {boarding['first_name']} {boarding['last_name']}
Phone: {boarding['phone'] or 'N/A'}
Email: {boarding['email'] or 'N/A'}

Pet: {boarding['pet_name']}
Type: {boarding['pet_type'].capitalize()}
Breed: {boarding['breed'] or 'N/A'}

Check-in: {boarding['check_in']}
Days Stay: {boarding['days_stay']}
Rate: ${'50' if boarding['pet_type'] == 'dog' else '40'} per day

Total Amount: ${boarding['amount_due']:.2f}
Grooming Service: {'Yes' if boarding['grooming_requested'] else 'No'}

Thank you for choosing Pet Boarding!
"""
        return invoice