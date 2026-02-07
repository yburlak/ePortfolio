# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Establish connection with pet_bag_db

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