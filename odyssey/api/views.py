from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .mongodb import get_db, serialize_mongodb_object
from datetime import datetime

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
        result = db.addresses.insert_one(address_data)
        created_address = db.addresses.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_address), status=status.HTTP_201_CREATED)

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
        status = request.query_params.get('status')
        
        query = {}
        if trial_id:
            query['trial_id'] = trial_id
        if site_id:
            query['$or'] = [{'origin': site_id}, {'destination': site_id}]
        if status:
            query['status'] = status
            
        shipments = list(db.shipments.find(query))
        return Response([serialize_mongodb_object(shipment) for shipment in shipments])

    def create(self, request):
        """POST /api/shipments/"""
        db = get_db()
        shipment_data = request.data
        shipment_data['created_at'] = datetime.utcnow()
        
        # Validate references
        if not db.sites.find_one({'site_id': shipment_data.get('origin')}):
            return Response({'error': 'Origin site not found'}, status=status.HTTP_400_BAD_REQUEST)
        if not db.sites.find_one({'site_id': shipment_data.get('destination')}):
            return Response({'error': 'Destination site not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        result = db.shipments.insert_one(shipment_data)
        created_shipment = db.shipments.find_one({'_id': result.inserted_id})
        return Response(serialize_mongodb_object(created_shipment), status=status.HTTP_201_CREATED)

class KitViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/kits/"""
        db = get_db()
        site_id = request.query_params.get('site_id')
        
        query = {}
        if site_id:
            query['site_id'] = site_id
            
        kits = list(db.kits.find(query))
        return Response([serialize_mongodb_object(kit) for kit in kits])

    @action(detail=False, methods=['get'])
    def inventory(self, request):
        """GET /api/kits/inventory/"""
        db = get_db()
        pipeline = [
            {
                '$group': {
                    '_id': '$site_id',
                    'total_kits': {'$sum': 1},
                    'available_kits': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'available']}, 1, 0]}
                    }
                }
            }
        ]
        inventory = list(db.kits.aggregate(pipeline))
        return Response(serialize_mongodb_object(inventory))

class ParcelViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/parcels/"""
        db = get_db()
        shipment_id = request.query_params.get('shipment_id')
        
        query = {}
        if shipment_id:
            query['shipment_id'] = shipment_id
            
        parcels = list(db.parcels.find(query))
        return Response([serialize_mongodb_object(parcel) for parcel in parcels])

class FailureViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/failures/"""
        db = get_db()
        shipment_id = request.query_params.get('shipment_id')
        
        query = {}
        if shipment_id:
            query['shipment_id'] = shipment_id
            
        failures = list(db.failures.find(query))
        return Response([serialize_mongodb_object(failure) for failure in failures])

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """GET /api/failures/analytics/"""
        db = get_db()
        pipeline = [
            {
                '$group': {
                    '_id': '$reason',
                    'count': {'$sum': 1},
                    'shipments': {'$push': '$shipment_id'}
                }
            }
        ]
        analytics = list(db.failures.aggregate(pipeline))
        return Response(serialize_mongodb_object(analytics))
