from django.urls import path
from .views import (
    OnlineProductionReportListView,
    OnlineProductionReportFormView,
    OnlineProductionReportEditView,
    OnlineProductionReportAPI,
    OnlineProductionReportDetailAPI,
    OnlineProductionReportDeleteView,
    DailyProductionReportListView,
    DailyProductionReportFormView,
    DailyProductionReportEditView,
    DailyProductionReportAPI,
    DailyProductionReportDetailAPI,
    DailyProductionReportDeleteView,
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

    #_______________Daily Production Report________________
    # List view
    path('daily-production-reports/', DailyProductionReportListView.as_view(), name='daily_production_report_list'),
    
    # Form views
    path('daily-production-report/', DailyProductionReportFormView.as_view(), name='daily_production_report'),
    path('daily-production-report/edit/<int:pk>/', DailyProductionReportEditView.as_view(), name='daily_production_report_edit'),
    
    # API endpoints
    path('api/daily-production-reports/', DailyProductionReportAPI.as_view(), name='daily_production_report_api'),
    path('api/daily-production-reports/<int:pk>/', DailyProductionReportDetailAPI.as_view(), name='daily_production_report_detail_api'),
    
    # Delete
    path('daily-production-report/delete/<int:pk>/', DailyProductionReportDeleteView.as_view(), name='daily_production_report_delete'),




    # path("total-production-report/", TotalProductionReportView.as_view(), name="total_production_report"),

]