import os
import django
from pathlib import Path

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'odyssey.settings')
django.setup()

# Now import Django models
from django.contrib.auth.models import User

def create_test_user():
    try:
        # Check if user already exists
        if User.objects.filter(username='testuser').exists():
            print("\n Test user already exists!")
            return
        
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            is_staff=True  # Allow access to admin site
        )
        print("\n✅ Test user created successfully!")
        print("\nCredentials:")
        print("Username: testuser")
        print("Password: testpass123")
    except Exception as e:
        print(f"\n❌ Error creating user: {str(e)}")

if __name__ == "__main__":
    create_test_user() 