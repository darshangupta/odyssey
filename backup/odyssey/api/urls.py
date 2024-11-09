from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TrialViewSet,
    DeviceViewSet,
    KitViewSet,
    ParcelViewSet,
    ShipmentViewSet,
    PatientViewSet,
    SiteViewSet,
    AddressViewSet,
    IoTDeviceViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'trials', TrialViewSet, basename='trial')
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'kits', KitViewSet, basename='kit')
router.register(r'parcels', ParcelViewSet, basename='parcel')
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'sites', SiteViewSet, basename='site')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'iot-devices', IoTDeviceViewSet, basename='iotdevice')

urlpatterns = [
    # Include all viewset routes
    path('', include(router.urls)),
] 