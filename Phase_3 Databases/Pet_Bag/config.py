# config.py
# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Configuration management for database and application settings
# 2026-02-07: Added authentication and security configuration

import os
from pathlib import Path
from dotenv import load_dotenv  # Add this import

# load environment variables from .env file
# this must be called BEFORE accessing os.getenv()
load_dotenv()

class Config:
    # database configuration (read from environment variables)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'pet_bag_db')
    
    # application configuration
    APP_NAME = "PetBag Boarding System"
    VERSION = "1.0.0"
    
    # session configuration
    SESSION_TIMEOUT = 1800  # 30 minutes in seconds
    
    # logging configuration
    LOG_FILE = "app.log"
    LOG_LEVEL = "INFO"

config = Config()