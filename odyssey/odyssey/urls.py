from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Handles admin URLs
    path('api/', include('api.urls')),  # Forwards all /api/ requests to api/urls.py
]