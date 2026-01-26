#!/usr/bin/env python3
"""
Setup script for Flask Weather Station
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages from requirements.txt"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if os.path.exists('.env'):
        print("✓ .env file already exists")
        return True
    
    if os.path.exists('env_example.txt'):
        try:
            with open('env_example.txt', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✓ Created .env file from template")
        print("⚠️  Please edit .env file with your API keys")
            return True
        except Exception as e:
            print(f"✗ Error creating .env file: {e}")
            return False
    else:
        print("✗ env_example.txt not found")
        return False

def main():
    """Main setup function"""
    print("Flask Weather Station - Setup")
    print("=" * 30)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    print("\n" + "=" * 30)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit the .env file with your API keys")
    print("2. Run: python app.py")
    print("3. Open http://localhost:5000 in your browser")
    print("\nFor detailed setup instructions, see README.md")

if __name__ == "__main__":
    main()
