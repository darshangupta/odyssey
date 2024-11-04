from rest_framework.routers import DefaultRouter
from .views import (
    ShipmentViewSet, TrialViewSet, SiteViewSet, 
    PatientViewSet, AddressViewSet, ContactPersonViewSet,
    KitViewSet, ParcelViewSet, FailureViewSet
)
from django.urls import path, include

router = DefaultRouter()
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'trials', TrialViewSet, basename='trial')
router.register(r'sites', SiteViewSet, basename='site')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'contact-persons', ContactPersonViewSet, basename='contact-person')
router.register(r'kits', KitViewSet, basename='kit')
router.register(r'parcels', ParcelViewSet, basename='parcel')
router.register(r'failures', FailureViewSet, basename='failure')

urlpatterns = [
    path('', include(router.urls)),
] 