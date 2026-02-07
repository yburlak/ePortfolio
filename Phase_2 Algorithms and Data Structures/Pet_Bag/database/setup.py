# database/setup.py
# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Create database and tables in MySQL
# 2026-01-31: Cascade delete implemented.

import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    def __init__(self):
        self.connection = None
    
    def connect(self, host="localhost", user="root", password="Tilin_Wolf123@", database="pet_bag_db"):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            print(f"Connected to database '{database}'")
            return True
        except Error as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

def setup_database():
    try:
        # connect to MySQL server 
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Tilin_Wolf123@"  # my password
        )
        
        cursor = connection.cursor()
        
        # create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS pet_bag_db")
        cursor.execute("USE pet_bag_db")
        
        # create Customer table 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customer (
                customer_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50),
                phone VARCHAR(20),
                email VARCHAR(100)
            )
        """)
        
        # create Pet table 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Pet (
                pet_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT NOT NULL,
                pet_name VARCHAR(50) NOT NULL,
                pet_type VARCHAR(10) NOT NULL,
                pet_age DECIMAL(4,1),
                breed VARCHAR(50),
                weight DECIMAL(5,2) DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
                ON DELETE CASCADE
            )
        """)
        
        # create Boarding table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Boarding (
                boarding_id INT AUTO_INCREMENT PRIMARY KEY,
                pet_id INT NOT NULL,
                check_in DATE NOT NULL,
                check_out DATE,
                days_stay INT NOT NULL,
                amount_due DECIMAL(10,2) NOT NULL,
                grooming_requested BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (pet_id) REFERENCES Pet(pet_id)
                ON DELETE CASCADE
            )
        """)
        
        # create Grooming table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Grooming (
                grooming_id INT AUTO_INCREMENT PRIMARY KEY,
                boarding_id INT,
                pet_id INT NOT NULL,
                service_date DATE NOT NULL,
                service_type VARCHAR(50),
                price DECIMAL(10,2),
                FOREIGN KEY (pet_id) REFERENCES Pet(pet_id)
                ON DELETE CASCADE,
                FOREIGN KEY (boarding_id) REFERENCES Boarding(boarding_id)
                ON DELETE SET NULL
            )
        """)
        
        connection.commit()
        print(" Database 'pet_bag_db' created successfully!")
        print(" Tables created: Customer, Pet, Boarding, Grooming")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f" Setup error: {e}")

if __name__ == "__main__":
    setup_database()