from django.urls import path
from .views import DashboardView

urlpatterns = [
    # IOT Dashboard with die cards
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # API endpoint to refresh die cards data
    path('dashboard/refresh/', DashboardView.as_view(), name='dashboard_refresh'),
]