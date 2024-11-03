from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .mongodb import get_db, serialize_mongodb_object
from datetime import datetime

class ShipmentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /api/shipments/"""
        db = get_db()
        trial_id = request.query_params.get('trial_id')
        
        query = {}
        if trial_id:
            query['trial_id'] = trial_id
            
        shipments = list(db.shipments.find(query))
        return Response([serialize_mongodb_object(ship) for ship in shipments])

    def create(self, request):
        """POST /api/shipments/"""
        db = get_db()
        shipment_data = request.data
        shipment_data['created_at'] = datetime.utcnow()
        
        result = db.shipments.insert_one(shipment_data)
        created_shipment = db.shipments.find_one({'_id': result.inserted_id})
        return Response(
            serialize_mongodb_object(created_shipment), 
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None):
        """GET /api/shipments/{tracking_number}/"""
        db = get_db()
        shipment = db.shipments.find_one({'tracking_number': pk})
        
        if not shipment:
            return Response(
                {'error': 'Shipment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(serialize_mongodb_object(shipment))

    def update(self, request, pk=None):
        """PUT /api/shipments/{tracking_number}/"""
        db = get_db()
        update_data = request.data
        update_data['updated_at'] = datetime.utcnow()
        
        result = db.shipments.update_one(
            {'tracking_number': pk},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return Response(
                {'error': 'Shipment not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        updated_shipment = db.shipments.find_one({'tracking_number': pk})
        return Response(serialize_mongodb_object(updated_shipment))

    @action(detail=False, methods=['get'])
    def saved_shipment_information(self, request):
        """GET /api/shipments/saved_shipment_information/"""
        db = get_db()
        username = request.query_params.get('username')
        shipments = list(db.shipments.find({
            'notification_emails': username
        }))
        return Response([serialize_mongodb_object(ship) for ship in shipments])

    @action(detail=False, methods=['post'])
    def save_created_shipment(self, request):
        """POST /api/shipments/save_created_shipment/"""
        db = get_db()
        shipment_data = request.data
        shipment_data['created_at'] = datetime.utcnow()
        
        result = db.shipments.insert_one(shipment_data)
        created_shipment = db.shipments.find_one({'_id': result.inserted_id})
        return Response(
            serialize_mongodb_object(created_shipment), 
            status=status.HTTP_201_CREATED
        )
