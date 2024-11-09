from django.db import models

# Create your models here.

class Site(models.Model):
    site_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    address = models.ForeignKey('Address', on_delete=models.PROTECT)
    contact_person = models.ForeignKey('ContactPerson', on_delete=models.SET_NULL, null=True)
    associated_trials = models.ManyToManyField('Trial', related_name='trial_sites')
    kit_inventory = models.JSONField(default=dict)  # Store current kit inventory
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.site_id})"

class Trial(models.Model):
    trial_id = models.CharField(max_length=100, unique=True)
    associated_sites = models.ManyToManyField(Site, related_name='site_trials')
    associated_patients = models.ManyToManyField('Patient')
    diagnostic_kits_template = models.JSONField()  # Store kit configuration, matches parcel template IDs
    default_send_address = models.ForeignKey('Address', null=True, on_delete=models.SET_NULL, related_name='trial_send_address')
    default_receive_address = models.ForeignKey('Address', null=True, on_delete=models.SET_NULL, related_name='trial_receive_address')

class Device(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=100)
    device_name = models.CharField(max_length=100)
    expiration_date = models.DateTimeField()
    batch_no = models.CharField(max_length=100)
    sample_type = models.CharField(max_length=50)  # Blood, Saliva, Urine, Other
    temp_range = models.CharField(max_length=100)
    is_hazardous = models.BooleanField(default=False)

class IoTDevice(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=100)
    battery_life = models.CharField(max_length=50)
    cycle_count = models.IntegerField(default=0)
    exists = models.BooleanField(default=False)

class Kit(models.Model):
    kit_id = models.CharField(max_length=100, unique=True)
    kit_name = models.CharField(max_length=100)
    device = models.ForeignKey(Device, on_delete=models.PROTECT)
    iot_device = models.ForeignKey(IoTDevice, null=True, on_delete=models.SET_NULL)
    return_box_dimensions = models.CharField(max_length=50)  # Format: LxWxH in inches
    return_box_weight = models.DecimalField(max_digits=5, decimal_places=2)  # in lbs
    is_template = models.BooleanField(default=False)

class Parcel(models.Model):
    dimensions = models.CharField(max_length=50)  # Format: LxWxH in inches
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # in lbs
    total_pieces = models.IntegerField()
    contents = models.JSONField()  # Store array of kit IDs and quantities
    additional_items = models.JSONField(null=True)  # Store other items
    is_template = models.BooleanField(default=False)

class Patient(models.Model):
    patient_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    associated_trials = models.ManyToManyField(Trial)
    associated_sites = models.ManyToManyField(Site, related_name='site_patients')
    scheduled_collection_dates = models.JSONField()  # Store as array of dates
    contact_person = models.ForeignKey('ContactPerson', on_delete=models.SET_NULL, null=True)

class ContactPerson(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    role = models.CharField(max_length=50)  # e.g., "Nurse", "Doctor", etc.
    relationship = models.CharField(max_length=50)  # e.g., "Parent", "Guardian", etc.

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
    failures = models.JSONField(null=True)  # Store array of failure modes
    parcels = models.ManyToManyField(Parcel)

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
