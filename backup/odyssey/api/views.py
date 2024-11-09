from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .mongodb import get_db, serialize_mongodb_object
from datetime import datetime
from .validators import *
from typing import List, Dict
import asyncio

class TrialViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/trials/"""
        db = get_db()
        trials = list(db.trials.find({}))
        return Response([serialize_mongodb_object(trial) for trial in trials])

    def create(self, request):
        """POST /api/trials/"""
        db = get_db()
        trial_data = request.data
        trial_data['created_at'] = datetime.utcnow()
        
        result = db.trials.insert_one(trial_data)
        created_trial = db.trials.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_trial), status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """GET /api/trials/{trial_id}/"""
        db = get_db()
        trial = db.trials.find_one({'trial_id': pk})
        if not trial:
            return Response({'error': 'Trial not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_mongodb_object(trial))

    @action(detail=True, methods=['get'])
    def associated_sites(self, request, pk=None):
        """GET /api/trials/{trial_id}/associated_sites/"""
        db = get_db()
        sites = list(db.sites.find({'associated_trials': pk}))
        return Response([serialize_mongodb_object(site) for site in sites])

    @action(detail=True, methods=['post'])
    def bulk_add_sites(self, request, pk=None):
        """POST /api/trials/{trial_id}/bulk_add_sites/"""
        db = get_db()
        site_ids: List[str] = request.data.get('site_ids', [])
        
        # Validate all sites exist
        existing_sites = db.sites.count_documents({'site_id': {'$in': site_ids}})
        if existing_sites != len(site_ids):
            return Response({'error': 'One or more sites not found'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        result = db.trials.update_one(
            {'trial_id': pk},
            {'$addToSet': {'associated_sites': {'$each': site_ids}}}
        )
        
        updated_trial = db.trials.find_one({'trial_id': pk})
        return Response(serialize_mongodb_object(updated_trial))

    @action(detail=True, methods=['post'])
    def manage_relationships(self, request, pk=None):
        """POST /api/trials/{trial_id}/manage_relationships/"""
        db = get_db()
        add_sites = request.data.get('add_sites', [])
        remove_sites = request.data.get('remove_sites', [])
        add_patients = request.data.get('add_patients', [])
        remove_patients = request.data.get('remove_patients', [])
        
        updates = {}
        if add_sites:
            updates['$addToSet'] = {'associated_sites': {'$each': add_sites}}
        if remove_sites:
            updates['$pullAll'] = {'associated_sites': remove_sites}
        if add_patients:
            updates['$addToSet'] = {'associated_patients': {'$each': add_patients}}
        if remove_patients:
            updates['$pullAll'] = {'associated_patients': remove_patients}
            
        result = db.trials.update_one({'trial_id': pk}, updates)
        updated_trial = db.trials.find_one({'trial_id': pk})
        return Response(serialize_mongodb_object(updated_trial))

class PatientViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/patients/"""
        db = get_db()
        trial_id = request.query_params.get('trial_id')
        site_id = request.query_params.get('site_id')
        
        query = {}
        if trial_id:
            query['associated_trials'] = trial_id
        if site_id:
            query['associated_sites'] = site_id
            
        patients = list(db.patients.find(query))
        return Response([serialize_mongodb_object(patient) for patient in patients])

    def create(self, request):
        """POST /api/patients/"""
        db = get_db()
        patient_data = request.data
        patient_data['created_at'] = datetime.utcnow()
        
        result = db.patients.insert_one(patient_data)
        created_patient = db.patients.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_patient), status=status.HTTP_201_CREATED)

class SiteViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/sites/"""
        db = get_db()
        trial_id = request.query_params.get('trial_id')
        query = {'associated_trials': trial_id} if trial_id else {}
        sites = list(db.sites.find(query))
        return Response([serialize_mongodb_object(site) for site in sites])

    def create(self, request):
        """POST /api/sites/"""
        db = get_db()
        site_data = request.data
        site_data['created_at'] = datetime.utcnow()
        
        result = db.sites.insert_one(site_data)
        created_site = db.sites.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_site), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def kit_inventory(self, request, pk=None):
        """GET /api/sites/{site_id}/kit_inventory/"""
        db = get_db()
        site = db.sites.find_one({'site_id': pk})
        if not site:
            return Response({'error': 'Site not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_mongodb_object(site.get('associated_kits', {})))

class AddressViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/addresses/"""
        db = get_db()
        addresses = list(db.addresses.find({}))
        return Response([serialize_mongodb_object(addr) for addr in addresses])

    def create(self, request):
        """POST /api/addresses/"""
        db = get_db()
        address_data = request.data
        
        # Validate postal code
        if not validate_postal_code(
            address_data.get('postal_code', ''),
            address_data.get('country', 'US')
        ):
            return Response(
                {'error': 'Invalid postal code format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = db.addresses.insert_one(address_data)
        created_address = db.addresses.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_address))

class ContactPersonViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/contact-persons/"""
        db = get_db()
        site_id = request.query_params.get('site_id')
        query = {'associated_sites': site_id} if site_id else {}
        contacts = list(db.contact_persons.find(query))
        return Response([serialize_mongodb_object(contact) for contact in contacts])

    def create(self, request):
        """POST /api/contact-persons/"""
        db = get_db()
        contact_data = request.data
        result = db.contact_persons.insert_one(contact_data)
        created_contact = db.contact_persons.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_contact), status=status.HTTP_201_CREATED)

class ShipmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/shipments/"""
        db = get_db()
        trial_id = request.query_params.get('trial_id')
        site_id = request.query_params.get('site_id')
        status_param = request.query_params.get('status')
        failure_mode = request.query_params.get('failure_mode')
        
        query = {}
        if trial_id:
            query['trial_id'] = trial_id
        if site_id:
            query['$or'] = [{'origin': site_id}, {'destination': site_id}]
        if status_param:
            query['status'] = status_param
        if failure_mode:
            query['failures'] = failure_mode
            
        shipments = list(db.shipments.find(query))
        return Response([serialize_mongodb_object(shipment) for shipment in shipments])

    def create(self, request):
        """POST /api/shipments/"""
        db = get_db()
        shipment_data = request.data
        shipment_data['created_at'] = datetime.utcnow()
        
        # Initialize empty failures array if not provided
        if 'failures' not in shipment_data:
            shipment_data['failures'] = []
        
        # Validate references
        if not db.sites.find_one({'site_id': shipment_data.get('origin')}):
            return Response({'error': 'Origin site not found'}, status=status.HTTP_400_BAD_REQUEST)
        if not db.sites.find_one({'site_id': shipment_data.get('destination')}):
            return Response({'error': 'Destination site not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        result = db.shipments.insert_one(shipment_data)
        created_shipment = db.shipments.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_shipment), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_failure(self, request, pk=None):
        """POST /api/shipments/{tracking_number}/add_failure/"""
        db = get_db()
        shipment = db.shipments.find_one({'tracking_number': pk})
        if not shipment:
            return Response({'error': 'Shipment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        failure = request.data.get('failure')
        if not failure:
            return Response({'error': 'Failure details required'}, status=status.HTTP_400_BAD_REQUEST)
            
        result = db.shipments.update_one(
            {'tracking_number': pk},
            {'$push': {'failures': failure}}
        )
        
        updated_shipment = db.shipments.find_one({'tracking_number': pk})
        return Response(serialize_mongodb_object(updated_shipment))

    @action(detail=False, methods=['get'])
    def failure_analytics(self, request):
        """GET /api/shipments/failure_analytics/"""
        db = get_db()
        pipeline = [
            {'$unwind': '$failures'},
            {
                '$group': {
                    '_id': '$failures',
                    'count': {'$sum': 1},
                    'shipments': {'$push': '$tracking_number'}
                }
            }
        ]
        analytics = list(db.shipments.aggregate(pipeline))
        return Response(serialize_mongodb_object(analytics))

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """POST /api/shipments/{tracking_number}/update_status/"""
        db = get_db()
        new_status = request.data.get('status')
        if new_status not in ['PENDING', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            
        result = db.shipments.update_one(
            {'tracking_number': pk},
            {'$set': {'status': new_status}}
        )
        if result.modified_count == 0:
            return Response({'error': 'Shipment not found'}, status=status.HTTP_404_NOT_FOUND)
            
        updated_shipment = db.shipments.find_one({'tracking_number': pk})
        return Response(serialize_mongodb_object(updated_shipment))

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """POST /api/shipments/bulk_create/"""
        db = get_db()
        shipments_data = request.data.get('shipments', [])
        
        # Validate all shipments
        for shipment in shipments_data:
            if not db.sites.find_one({'site_id': shipment.get('origin')}):
                return Response(
                    {'error': f'Origin site not found for shipment {shipment.get("tracking_number")}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not db.sites.find_one({'site_id': shipment.get('destination')}):
                return Response(
                    {'error': f'Destination site not found for shipment {shipment.get("tracking_number")}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Add timestamps and initialize failures
        for shipment in shipments_data:
            shipment['created_at'] = datetime.utcnow()
            shipment['failures'] = []
        
        result = db.shipments.insert_many(shipments_data)
        created_shipments = list(db.shipments.find(
            {'_id': {'$in': result.inserted_ids}}
        ))
        return Response(serialize_mongodb_object(created_shipments))

class KitViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/kits/"""
        db = get_db()
        site_id = request.query_params.get('site_id')
        is_template = request.query_params.get('is_template')
        
        query = {}
        if site_id:
            query['site_id'] = site_id
        if is_template is not None:
            query['is_template'] = bool(is_template)
            
        kits = list(db.kits.find(query))
        return Response([serialize_mongodb_object(kit) for kit in kits])

    def create(self, request):
        """POST /api/kits/"""
        db = get_db()
        kit_data = request.data
        
        # Validate dimensions
        if not validate_dimensions(kit_data.get('return_box_dimensions', '')):
            return Response(
                {'error': 'Invalid dimensions format. Use LxWxHin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate device existence
        if not db.devices.find_one({'device_id': kit_data.get('device_id')}):
            return Response(
                {'error': 'Device not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate IoT device if provided
        if 'iot_device' in kit_data:
            iot_device = kit_data['iot_device']
            if not db.iot_devices.find_one({'device_id': iot_device.get('device_id')}):
                return Response(
                    {'error': 'IoT device not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        result = db.kits.insert_one(kit_data)
        created_kit = db.kits.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_kit))

    @action(detail=True, methods=['get'])
    def device_details(self, request, pk=None):
        """GET /api/kits/{kit_id}/device_details/"""
        db = get_db()
        kit = db.kits.find_one({'kit_id': pk})
        if not kit:
            return Response({'error': 'Kit not found'}, status=status.HTTP_404_NOT_FOUND)
            
        device = db.devices.find_one({'device_id': kit['device_id']})
        iot_device = db.iot_devices.find_one({'device_id': kit.get('iot_device', {}).get('device_id')})
        
        return Response({
            'kit': serialize_mongodb_object(kit),
            'device': serialize_mongodb_object(device),
            'iot_device': serialize_mongodb_object(iot_device)
        })

class ParcelViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/parcels/"""
        db = get_db()
        shipment_id = request.query_params.get('shipment_id')
        is_template = request.query_params.get('is_template')
        
        query = {}
        if shipment_id:
            query['shipment_id'] = shipment_id
        if is_template is not None:
            query['is_template'] = bool(is_template)
            
        parcels = list(db.parcels.find(query))
        return Response([serialize_mongodb_object(parcel) for parcel in parcels])

    def create(self, request):
        """POST /api/parcels/"""
        db = get_db()
        parcel_data = request.data
        
        # Ensure dimensions are in inches and weight in lbs
        if 'dimensions' in parcel_data and not parcel_data['dimensions'].lower().endswith('in'):
            return Response({'error': 'Dimensions must be in inches'}, status=status.HTTP_400_BAD_REQUEST)
            
        result = db.parcels.insert_one(parcel_data)
        created_parcel = db.parcels.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_parcel), status=status.HTTP_201_CREATED)

class DeviceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        db = get_db()
        manufacturer = request.query_params.get('manufacturer')
        sample_type = request.query_params.get('sample_type')
        
        query = {}
        if manufacturer:
            query['manufacturer'] = manufacturer
        if sample_type:
            query['sample_type'] = sample_type
            
        devices = list(db.devices.find(query))
        return Response([serialize_mongodb_object(device) for device in devices])

    def create(self, request):
        db = get_db()
        device_data = request.data
        if 'expiration_date' in device_data:
            device_data['expiration_date'] = datetime.fromisoformat(device_data['expiration_date'])
        
        result = db.devices.insert_one(device_data)
        created_device = db.devices.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_device), status=status.HTTP_201_CREATED)

class IoTDeviceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        db = get_db()
        exists = request.query_params.get('exists')
        query = {'exists': bool(exists)} if exists is not None else {}
        
        iot_devices = list(db.iot_devices.find(query))
        return Response([serialize_mongodb_object(device) for device in iot_devices])

    def create(self, request):
        db = get_db()
        device_data = request.data
        device_data['cycle_count'] = device_data.get('cycle_count', 0)
        device_data['exists'] = device_data.get('exists', False)
        
        result = db.iot_devices.insert_one(device_data)
        created_device = db.iot_devices.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_device), status=status.HTTP_201_CREATED)
