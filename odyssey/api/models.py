from django.db import models

# Create your models here.

class Trial(models.Model):
    trial_id = models.CharField(max_length=100, unique=True)
    associated_sites = models.ManyToManyField('Site')
    associated_patients = models.ManyToManyField('Patient')
    diagnostic_kits_template = models.JSONField()  # Store kit configuration
    default_address = models.ForeignKey('Address', null=True, on_delete=models.SET_NULL)

class Patient(models.Model):
    patient_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    associated_trials = models.ManyToManyField(Trial)
    associated_sites = models.ManyToManyField('Site')
    scheduled_collection_dates = models.JSONField()  # Store as array of dates
    contact_person = models.ForeignKey('ContactPerson', on_delete=models.SET_NULL, null=True)

class Site(models.Model):
    site_id = models.CharField(max_length=100, unique=True)
    address = models.ForeignKey('Address', on_delete=models.PROTECT)
    associated_trials = models.ManyToManyField(Trial)
    kit_inventory_count = models.IntegerField(default=0)
    inventory_threshold = models.IntegerField(default=10)
    contact_person = models.ForeignKey('ContactPerson', on_delete=models.SET_NULL, null=True)

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    tracking_number = models.CharField(max_length=100, unique=True)
    trial = models.ForeignKey(Trial, on_delete=models.PROTECT)
    origin = models.ForeignKey('Address', related_name='shipments_from', on_delete=models.PROTECT)
    destination = models.ForeignKey('Address', related_name='shipments_to', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    carrier = models.CharField(max_length=50)
    service_type = models.CharField(max_length=50)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    pickup_date = models.DateTimeField(null=True)
    expected_delivery = models.DateTimeField(null=True)
    actual_delivery = models.DateTimeField(null=True)
    requires_signature = models.BooleanField(default=False)
    hold_at_location = models.BooleanField(default=False)
    sample_ids = models.JSONField(null=True)  # Store array of sample IDs
    notification_emails = models.JSONField(null=True)  # Store array of emails

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

class ContactPerson(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    role = models.CharField(max_length=50)  # e.g., "Nurse", "Parent", etc.
