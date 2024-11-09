import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the absolute path to your project root
project_root = str(Path(__file__).resolve().parent.parent)

# Add the project root to Python path
sys.path.insert(0, project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'odyssey.odyssey.settings')

# Debug prints
print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")
print(f"Looking for settings at: odyssey/odyssey/settings.py")

import django
django.setup()

from django.contrib.auth.models import User

def create_test_user():
    try:
        # Check if user already exists
        if User.objects.filter(username='testuser').exists():
            print("\n⚠️  Test user already exists!")
            return
        
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            is_staff=True
        )
        print("\n✅ Test user created successfully!")
        print("\nCredentials:")
        print("Username: testuser")
        print("Password: testpass123")
    except Exception as e:
        print(f"\n❌ Error creating user: {str(e)}")

if __name__ == "__main__":
    create_test_user() 