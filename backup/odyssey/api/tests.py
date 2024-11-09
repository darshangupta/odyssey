import pytest
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .mongodb import get_db
from django.contrib.auth.models import User

# Mark this as a Django test
pytestmark = pytest.mark.django_db

class APIEndpointTests(APITestCase):
    def setUp(self):
        # Create test user for authentication
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.db = get_db()
        
        # Clean up any existing test data
        self.db.sites.delete_many({'site_id': {'$in': ['SITE001', 'SITE002']}})
        self.db.shipments.delete_many({'tracking_number': {'$in': ['SHIP001', 'SHIP002']}})
        
        # Create test shipment data
        self.test_shipment = {
            "tracking_number": "SHIP001",
            "origin": "SITE001",
            "destination": "SITE002",
            "trial_id": "TRIAL001",
            "status": "in_transit",
            "carrier": "FedEx",
            "service_type": "Express",
            "created_at": "2024-01-20T10:00:00Z"
        }
        
        # Create test site data
        self.test_sites = [
            {
                "site_id": "SITE001",
                "name": "Boston Research Center",
                "associated_trials": ["TRIAL001"]
            },
            {
                "site_id": "SITE002",
                "name": "SF Research Center",
                "associated_trials": ["TRIAL001"]
            }
        ]
        
        # Insert test data
        try:
            self.db.sites.insert_many(self.test_sites)
            self.db.shipments.insert_one(self.test_shipment)
        except Exception as e:
            print(f"Setup error: {e}")
            self.tearDown()
            raise

    def test_shipment_endpoints(self):
        """Test basic shipment endpoints"""
        # Test GET /api/shipments/
        url = reverse('shipment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("GET /api/shipments/ - Success")
        
        # Test shipment creation
        new_shipment = {
            "tracking_number": "SHIP002",
            "origin": "SITE001",
            "destination": "SITE002",
            "trial_id": "TRIAL001",
            "status": "pending"
        }
        response = self.client.post(url, new_shipment, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("POST /api/shipments/ - Success")

    def test_site_filtering(self):
        """Test filtering shipments by site"""
        url = reverse('shipment-list')
        response = self.client.get(f"{url}?site_id=SITE001")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        print("GET /api/shipments/?site_id=SITE001 - Success")

    def tearDown(self):
        # Clean up test data
        try:
            self.db.shipments.delete_many({'tracking_number': {'$in': ['SHIP001', 'SHIP002']}})
            self.db.sites.delete_many({'site_id': {'$in': ['SITE001', 'SITE002']}})
            # Clean up test user
            self.user.delete()
        except Exception as e:
            print(f"Teardown error: {e}")
