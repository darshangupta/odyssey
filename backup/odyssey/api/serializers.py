from rest_framework import serializers
from .models import Trial, Patient, Site, Shipment, Address, ContactPerson

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'state', 'postal_code', 'country']

    def validate_postal_code(self, value):
        """
        Validate postal code format (basic example)
        """
        if len(value) < 5:
            raise serializers.ValidationError("Postal code must be at least 5 characters")
        return value

class ContactPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPerson
        fields = ['id', 'name', 'email', 'phone_number', 'role']

    def validate_phone_number(self, value):
        """
        Validate phone number format (basic example)
        """
        # Remove any non-numeric characters
        cleaned_number = ''.join(filter(str.isdigit, value))
        if len(cleaned_number) < 10:
            raise serializers.ValidationError("Phone number must have at least 10 digits")
        return value

    def validate_role(self, value):
        """
        Validate role is from accepted list
        """
        valid_roles = ['Nurse', 'Parent', 'Doctor', 'Site Manager', 'Trial Coordinator']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of: {', '.join(valid_roles)}")
        return value

class TrialSerializer(serializers.ModelSerializer):
    default_address = AddressSerializer(read_only=True)
    
    class Meta:
        model = Trial
        fields = [
            'trial_id', 
            'associated_sites', 
            'associated_patients',
            'diagnostic_kits_template',
            'default_address'
        ]

class PatientSerializer(serializers.ModelSerializer):
    contact_person = ContactPersonSerializer(read_only=True)
    associated_trials = TrialSerializer(many=True, read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'patient_id',
            'email',
            'phone_number',
            'associated_trials',
            'associated_sites',
            'scheduled_collection_dates',
            'contact_person'
        ]

class SiteSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    contact_person = ContactPersonSerializer(read_only=True)
    
    class Meta:
        model = Site
        fields = [
            'site_id',
            'address',
            'associated_trials',
            'kit_inventory_count',
            'inventory_threshold',
            'contact_person'
        ]

class ShipmentSerializer(serializers.ModelSerializer):
    origin = AddressSerializer(read_only=True)
    destination = AddressSerializer(read_only=True)
    trial = TrialSerializer(read_only=True)
    
    class Meta:
        model = Shipment
        fields = '__all__'

    def validate(self, data):
        """
        Custom validation for shipment data
        """
        if data.get('pickup_date') and data.get('expected_delivery'):
            if data['pickup_date'] >= data['expected_delivery']:
                raise serializers.ValidationError("Pickup date must be before expected delivery date")
        return data 