from django.urls import path
from .views import (
    DashboardView, 
    DashboardRecoveryTableAPI, 
    DashboardProductionTableAPI, 
    DashboardOrderTableAPI,
    # ... your other dashboard views
)

urlpatterns = [
    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # API endpoints
    path('api/dashboard-recovery-table/', DashboardRecoveryTableAPI.as_view(), name='dashboard_recovery_table_api'),
        path('api/dashboard-order-table/', DashboardOrderTableAPI.as_view(), name='dashboard-order-table-api'),
    path('api/dashboard-production-table/', DashboardProductionTableAPI.as_view(), name='dashboard_production_table_api'),
    
    # ... your other dashboard URLs
]