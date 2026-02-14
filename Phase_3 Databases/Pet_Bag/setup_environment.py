# setup_environment.py
# SNHU Course: CS-499 Capstone
# Student Name: Yana Burlak
# Description: Setup environment for first-time users

import os
import sys
from pathlib import Path

def setup_environment(): # setup environment variables for the app
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        print("Environment configuration file not found.")
        print(f"Creating from template: {env_example}")
        
        if env_example.exists():
            # copy .env.example to .env
            with open(env_example, 'r') as src:
                content = src.read()
            
            with open(env_file, 'w') as dst:
                dst.write(content)
            
            print("\nPlease edit the .env file with your database credentials.")
            print("Then run the application again.")
        else:
            print(f"Error: Template file {env_example} not found.")
            print("Please create a .env file with your database credentials.")
        
        return False
    
    # load environment variables
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    
    return True

if __name__ == "__main__":
    if setup_environment():
        print("Environment setup completed.")
        print("You can now run the application with: python main.py")
    else:
        sys.exit(1)