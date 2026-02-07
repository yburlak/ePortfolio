# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: BoardingService handles check-in operations for pets

from models.pet import Pet
from datetime import date
import mysql.connector

class BoardingService:
    
    @staticmethod
    def check_in_pet(db, pet_id, days_stay, grooming_requested=False):

        try:
            # get pet from database
            cursor = db.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Pet WHERE pet_id = %s", (pet_id,))
            pet_data = cursor.fetchone()
            cursor.close()
            
            if not pet_data:
                return False, "Pet not found"
            
            # create pet object
            pet = Pet(
                pet_id=pet_data['pet_id'],
                customer_id=pet_data['customer_id'],
                pet_name=pet_data['pet_name'],
                pet_type=pet_data['pet_type'],
                pet_age=pet_data['pet_age'],
                breed=pet_data['breed']
            )
            
            # check space availability 
            if pet.pet_type == "dog":
                if Pet.dog_spaces <= 0:
                    return False, "No spaces available for dogs"
                Pet.dog_spaces -= 1
            elif pet.pet_type == "cat":
                if Pet.cat_spaces <= 0:
                    return False, "No spaces available for cats"
                Pet.cat_spaces -= 1
            else:
                return False, "Invalid pet type"
            
            #TODO:Calculate amount due needs to be dynamic
            amount_due = 50 * days_stay if pet.pet_type == "dog" else 40 * days_stay
            
            # save boarding record
            cursor = db.connection.cursor()
            sql = """
                INSERT INTO Boarding (pet_id, check_in, days_stay, amount_due, grooming_requested)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (pet.pet_id, date.today(), days_stay, amount_due, grooming_requested))
            
            # if grooming requested for dog staying 2+ days
            if grooming_requested and pet.pet_type == "dog" and days_stay >= 2:
                # create grooming record
                grooming_sql = """
                    INSERT INTO Grooming (pet_id, service_date, service_type, price)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(grooming_sql, (pet.pet_id, date.today(), "Full Grooming", 30.00))
            
            db.connection.commit()
            cursor.close()
            
            # build success message
            message = f"{pet.pet_name} checked in successfully!\n"
            message += f"Space assigned. Amount due: ${amount_due:.2f}"
            
            if grooming_requested and pet.pet_type == "dog" and days_stay >= 2:
                message += "\nGrooming service scheduled."
            elif grooming_requested:
                message += "\nNote: Grooming only available for dogs staying 2+ days."
            
            return True, message
            
        except Exception as e:
            # handle any error
            if 'pet' in locals() and pet.pet_type == "dog":
                Pet.dog_spaces += 1
            elif 'pet' in locals() and pet.pet_type == "cat":
                Pet.cat_spaces += 1
            
            return False, f"Check-in failed: {str(e)}"
    
    @staticmethod
    def get_available_spaces():
    
        return {
            "dog_spaces": Pet.dog_spaces,
            "cat_spaces": Pet.cat_spaces
        }
    
    @staticmethod
    def get_current_boardings(db):
        
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, p.pet_name, p.pet_type, c.first_name, c.last_name
            FROM Boarding b
            JOIN Pet p ON b.pet_id = p.pet_id
            JOIN Customer c ON p.customer_id = c.customer_id
            WHERE b.check_out IS NULL
            ORDER BY b.check_in DESC
        """)
        boardings = cursor.fetchall()
        cursor.close()
        return boardings