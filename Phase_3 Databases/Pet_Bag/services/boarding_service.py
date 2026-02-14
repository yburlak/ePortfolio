# services/boarding_service.py
# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: BoardingService handles check-in operations for 
# 2026-01-31: Added weight-based grooming cost calculation and updated boarding prices

from models.pet import Pet
from datetime import date

class BoardingService:
    TOTAL_DOG_SPACES = 30
    TOTAL_CAT_SPACES = 12
    
    # boarding prices per day
    BOARDING_PRICES = {
        'dog': 30,
        'cat': 25
    }
    
    # grooming price tiers by weight for dogs
    GROOMING_PRICES = {
        'small': {'min': 2, 'max': 20, 'price': 50},
        'medium': {'min': 21, 'max': 50, 'price': 70},
        'large': {'min': 51, 'max': 100, 'price': 90},
        'extra_large': {'min': 101, 'max': float('inf'), 'price': 110}
    }
    
    #calculate grooming price based on dog weight
    @staticmethod
    def calculate_grooming_price(weight):
        
        if weight < 2:  # Below minimum weight
            return 0  # No grooming for very small dogs
        
        for tier, details in BoardingService.GROOMING_PRICES.items():
            if details['min'] <= weight <= details['max']:
                return details['price']
        
        # Default to extra large if weight exceeds all ranges
        return BoardingService.GROOMING_PRICES['extra_large']['price']
    
    @staticmethod
    def check_in_pet(db, pet_id, days_stay, grooming_requested=False):
        try:
            # get pet from database
            cursor = db.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Pet WHERE pet_id = %s", (pet_id,))
            pet_data = cursor.fetchone()
            
            if not pet_data:
                cursor.close()
                return False, "Pet not found"
            
            pet_type = pet_data['pet_type'].lower()
            
            # check space availability from database
            occupied = Pet.get_occupied_spaces(db)
            
            if pet_type == "dog":
                if occupied.get('dog', 0) >= BoardingService.TOTAL_DOG_SPACES:
                    cursor.close()
                    return False, "No spaces available for dogs"
            elif pet_type == "cat":
                if occupied.get('cat', 0) >= BoardingService.TOTAL_CAT_SPACES:
                    cursor.close()
                    return False, "No spaces available for cats"
            else:
                cursor.close()
                return False, "Invalid pet type"
            
            # calculate boarding amount due
            boarding_price = BoardingService.BOARDING_PRICES.get(pet_type, 0)
            boarding_amount = boarding_price * days_stay
            
            # calculate total amount due
            total_amount_due = boarding_amount
            
            # save boarding record
            sql = """
                INSERT INTO Boarding (pet_id, check_in, days_stay, amount_due, grooming_requested)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (pet_id, date.today(), days_stay, total_amount_due, grooming_requested))
            boarding_id = cursor.lastrowid
            
            # if grooming requested for dog staying 2+ days
            if grooming_requested and pet_type == "dog" and days_stay >= 2:
                # calculate grooming price based on weight
                grooming_price = BoardingService.calculate_grooming_price(pet_data.get('weight', 0))
                
                if grooming_price > 0:
                    # update boarding amount to include grooming
                    total_with_grooming = boarding_amount + grooming_price
                    cursor.execute("""
                        UPDATE Boarding 
                        SET amount_due = %s 
                        WHERE boarding_id = %s
                    """, (total_with_grooming, boarding_id))
                    
                    # create grooming record
                    grooming_sql = """
                        INSERT INTO Grooming (boarding_id, pet_id, service_date, service_type, price)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(grooming_sql, (boarding_id, pet_id, date.today(), "Full Grooming", grooming_price))
            
            db.connection.commit()
            cursor.close()
            
            # build success message
            message = f"{pet_data['pet_name']} checked in successfully!\n"
            message += f"Space assigned. Boarding amount: ${boarding_amount:.2f}"
            
            if grooming_requested and pet_type == "dog" and days_stay >= 2:
                grooming_price = BoardingService.calculate_grooming_price(pet_data.get('weight', 0))
                if grooming_price > 0:
                    message += f"\nGrooming service scheduled: ${grooming_price:.2f}"
                    message += f"\nTotal amount due: ${boarding_amount + grooming_price:.2f}"
                else:
                    message += "\nNote: Dog is too small for grooming (minimum 2lbs required)"
            elif grooming_requested:
                if pet_type != "dog":
                    message += "\nNote: Grooming only available for dogs"
                elif days_stay < 2:
                    message += "\nNote: Grooming only available for dogs staying 2+ days"
            
            return True, message
            
        except Exception as e:
            # handle any error
            return False, f"Check-in failed: {str(e)}"
    
    # calculate available spaces from database
    @staticmethod
    def get_available_spaces(db):
        
        occupied = Pet.get_occupied_spaces(db)
        
        return {
            "dog_spaces": BoardingService.TOTAL_DOG_SPACES - occupied.get('dog', 0),
            "cat_spaces": BoardingService.TOTAL_CAT_SPACES - occupied.get('cat', 0)
        }
    
    @staticmethod
    def get_current_boardings(db):
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, p.pet_name, p.pet_type, p.weight, c.first_name, c.last_name
            FROM Boarding b
            JOIN Pet p ON b.pet_id = p.pet_id
            JOIN Customer c ON p.customer_id = c.customer_id
            WHERE b.check_out IS NULL
            ORDER BY b.check_in DESC
        """)
        boardings = cursor.fetchall()
        cursor.close()
        return boardings