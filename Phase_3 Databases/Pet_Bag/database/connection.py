# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Establish connection with pet_bag_db
# 2026-02-07: Updated to use configuration file

import mysql.connector
from mysql.connector import Error
from config import config

class DatabaseConnection:
    def __init__(self):
        self.connection = None
    
    def connect(self, database=None):
        try:
            self.connection = mysql.connector.connect(
                host=config.DB_HOST,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=database or config.DB_NAME
            )
            print(f"Connected to database '{database or config.DB_NAME}'")
            return True
        except Error as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")