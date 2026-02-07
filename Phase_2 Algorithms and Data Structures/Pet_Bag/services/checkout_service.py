# services/checkout_service.py
# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: CheckoutService handles check-out operations for pets and generates invoice
# 2026-01-31: Modified invoice output to show grooming charges if applicable

from datetime import date
from services.boarding_service import BoardingService

class CheckoutService:
    
    @staticmethod
    def check_out_pet(db, boarding_id):
        try:
            # get boarding record with grooming details
            cursor = db.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT b.*, p.pet_id, p.pet_name, p.pet_type, p.weight,
                       g.price as grooming_price
                FROM Boarding b
                JOIN Pet p ON b.pet_id = p.pet_id
                LEFT JOIN Grooming g ON b.boarding_id = g.boarding_id
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
            SELECT b.*, p.pet_name, p.pet_type, p.breed, p.weight,
                   c.first_name, c.last_name, c.phone, c.email,
                   g.price as grooming_price,
                   g.service_date as grooming_date
            FROM Boarding b
            JOIN Pet p ON b.pet_id = p.pet_id
            JOIN Customer c ON p.customer_id = c.customer_id
            LEFT JOIN Grooming g ON b.boarding_id = g.boarding_id
            WHERE b.boarding_id = %s
        """, (boarding_id,))
        
        boarding = cursor.fetchall()
        cursor.close()
        
        if not boarding or len(boarding) == 0:
            return None
        
        boarding = boarding[0]
        
        # calculate boarding amount based on pet type and days
        boarding_rate = BoardingService.BOARDING_PRICES.get(boarding['pet_type'].lower(), 0)
        boarding_amount = boarding_rate * boarding['days_stay']
        
        # get grooming price if needed
        grooming_price = boarding['grooming_price'] or 0
        grooming_text = ""
        
        if boarding['grooming_requested'] and boarding['pet_type'].lower() == 'dog':
            if grooming_price > 0:
                grooming_text = f"Grooming Service: Yes (${grooming_price:.2f})\n"
                # Determine grooming tier
                for tier, details in BoardingService.GROOMING_PRICES.items():
                    if details['min'] <= boarding['weight'] <= details['max']:
                        grooming_text += f"Grooming Tier: {tier.title()} (Weight: {boarding['weight']}lbs)\n"
                        break
            else:
                grooming_text = "Grooming Service: Requested but not applicable\n"
                if boarding['days_stay'] < 2:
                    grooming_text += "  (Minimum 2-day stay required)\n"
                elif boarding['weight'] < 2:
                    grooming_text += f"  (Minimum 2 lbs required, current: {boarding['weight']}lbs)\n"
        
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
Weight: {boarding['weight'] or 'N/A'} lbs

Check-in: {boarding['check_in']}
Days Stay: {boarding['days_stay']}
Rate: ${boarding_rate} per day
Boarding Amount: ${boarding_amount:.2f}

{grooming_text}
Total Amount: ${boarding['amount_due']:.2f}

Thank you for choosing Pet Boarding!
"""
        return invoice