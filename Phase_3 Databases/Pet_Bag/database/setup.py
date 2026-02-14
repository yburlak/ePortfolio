# database/setup.py
# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Create database and tables in MySQL
# 2026-01-31: Cascade delete implemented.
# 2026-02-07: Added users table and updated to use configuration

import mysql.connector
from mysql.connector import Error
from config import config
import hashlib

def setup_database():
    try:
        # connect to MySQL server using config
        connection = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        
        cursor = connection.cursor()
        
        # create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME}")
        cursor.execute(f"USE {config.DB_NAME}")
        
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
        
        # create Users table for authentication
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                password_changed_at TIMESTAMP NULL
            )
        """)
        
        # Create an admin user if none exists
        cursor.execute("SELECT COUNT(*) FROM Users")
        if cursor.fetchone()[0] == 0:
            # Default password: admin123 (should be changed on first login)
            default_password = "admin123"
            password_hash = hashlib.sha256(default_password.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO Users (username, password_hash, email, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s)
            """, ('admin', password_hash, 'admin@petbag.com', 'Admin', 'User'))
            print("Created default admin user (username: admin, password: admin123)")
        
        connection.commit()
        print(f" Database '{config.DB_NAME}' created successfully!")
        print(" Tables created: Customer, Pet, Boarding, Grooming, Users")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f" Setup error: {e}")

if __name__ == "__main__":
    setup_database()