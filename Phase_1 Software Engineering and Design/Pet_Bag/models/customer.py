# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Customer model class with CRUD operations for customer data

from database.connection import DatabaseConnection

class Customer:
    def __init__(self, customer_id=None, first_name="", last_name="", phone="", email=""):
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
    
    def save(self, db):
        cursor = db.connection.cursor()
        if self.customer_id:
            sql = "UPDATE Customer SET first_name=%s, last_name=%s, phone=%s, email=%s WHERE customer_id=%s"
            cursor.execute(sql, (self.first_name, self.last_name, self.phone, self.email, self.customer_id))
        else:
            sql = "INSERT INTO Customer (first_name, last_name, phone, email) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (self.first_name, self.last_name, self.phone, self.email))
            self.customer_id = cursor.lastrowid
        
        db.connection.commit()
        cursor.close()
        return self.customer_id
    
    def delete(self, db):
        cursor = db.connection.cursor()
        sql = "DELETE FROM Customer WHERE customer_id=%s"
        cursor.execute(sql, (self.customer_id,))
        db.connection.commit()
        cursor.close()
    
    @staticmethod
    def get_all(db):
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Customer ORDER BY last_name, first_name")
        customers = cursor.fetchall()
        cursor.close()
        return customers
    
    @staticmethod
    def create(db, customer_data):
    
        cursor = db.connection.cursor()
        sql = "INSERT INTO Customer (first_name, last_name, phone, email) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (
            customer_data.get('first_name', ''),
            customer_data.get('last_name', ''),
            customer_data.get('phone', ''),
            customer_data.get('email', '')
        ))
        db.connection.commit()
        customer_id = cursor.lastrowid
        cursor.close()
        return customer_id
    
    @staticmethod
    def update(db, customer_id, customer_data):
        
        cursor = db.connection.cursor()
        sql = "UPDATE Customer SET first_name=%s, last_name=%s, phone=%s, email=%s WHERE customer_id=%s"
        cursor.execute(sql, (
            customer_data.get('first_name', ''),
            customer_data.get('last_name', ''),
            customer_data.get('phone', ''),
            customer_data.get('email', ''),
            customer_id
        ))
        db.connection.commit()
        cursor.close()
        return True