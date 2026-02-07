# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Pet model class with CRUD operations for pet data

from database.connection import DatabaseConnection

class Pet:
    #TODO: change static variables
    dog_spaces = 30
    cat_spaces = 12
    
    def __init__(self, pet_id=None, customer_id=None, pet_name="", pet_type="", pet_age=0, breed="", weight=0):
        self.pet_id = pet_id
        self.customer_id = customer_id
        self.pet_name = pet_name
        self.pet_type = pet_type.lower()
        self.pet_age = pet_age
        self.breed = breed
        self.weight = weight
    
    def save(self, db):
        cursor = db.connection.cursor()
        if self.pet_id:
            sql = "UPDATE Pet SET pet_name=%s, pet_type=%s, pet_age=%s, breed=%s, weight=%s WHERE pet_id=%s"
            cursor.execute(sql, (self.pet_name, self.pet_type, self.pet_age, self.breed, self.weight, self.pet_id))
        else:
            sql = "INSERT INTO Pet (customer_id, pet_name, pet_type, pet_age, breed, weight) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (self.customer_id, self.pet_name, self.pet_type, self.pet_age, self.breed, self.weight))
            self.pet_id = cursor.lastrowid
        
        db.connection.commit()
        cursor.close()
        return self.pet_id
    
    @staticmethod
    def get_all(db):
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, c.first_name, c.last_name 
            FROM Pet p 
            JOIN Customer c ON p.customer_id = c.customer_id
            ORDER BY p.pet_name
        """)
        pets = cursor.fetchall()
        cursor.close()
        return pets
    
    @staticmethod
    def create(db, pet_data):

        cursor = db.connection.cursor()
        sql = "INSERT INTO Pet (customer_id, pet_name, pet_type, pet_age, breed, weight) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (
            pet_data.get('customer_id'),
            pet_data.get('pet_name', ''),
            pet_data.get('pet_type', ''),
            pet_data.get('pet_age', 0),
            pet_data.get('breed', ''),
            pet_data.get('weight', 0)
        ))
        db.connection.commit()
        pet_id = cursor.lastrowid
        cursor.close()
        return pet_id
    
    @staticmethod
    def update(db, pet_id, pet_data):
       
        cursor = db.connection.cursor()
        sql = "UPDATE Pet SET customer_id=%s, pet_name=%s, pet_type=%s, pet_age=%s, breed=%s, weight=%s WHERE pet_id=%s"
        cursor.execute(sql, (
            pet_data.get('customer_id'),
            pet_data.get('pet_name', ''),
            pet_data.get('pet_type', ''),
            pet_data.get('pet_age', 0),
            pet_data.get('breed', ''),
            pet_data.get('weight', 0),
            pet_id
        ))
        db.connection.commit()
        cursor.close()
        return True