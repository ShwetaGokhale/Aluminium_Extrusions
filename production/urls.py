from django.urls import path
from .views import (
    OnlineProductionReportListView,
    OnlineProductionReportFormView,
    OnlineProductionReportEditView,
    OnlineProductionReportAPI,
    OnlineProductionReportDetailAPI,
    OnlineProductionReportDeleteView
)

urlpatterns = [
    #_______________Online Production Report________________
    # List view
    path('online-production-reports/', OnlineProductionReportListView.as_view(), name='online_production_report_list'),
    
    # Form views
    path('online-production-report/', OnlineProductionReportFormView.as_view(), name='online_production_report'),
    path('online-production-report/edit/<int:pk>/', OnlineProductionReportEditView.as_view(), name='online_production_report_edit'),
    
    # API endpoints
    path('api/online-production-reports/', OnlineProductionReportAPI.as_view(), name='online_production_report_api'),
    path('api/online-production-reports/<int:pk>/', OnlineProductionReportDetailAPI.as_view(), name='online_production_report_detail_api'),
    
    # Delete
    path('online-production-report/delete/<int:pk>/', OnlineProductionReportDeleteView.as_view(), name='online_production_report_delete'),
]