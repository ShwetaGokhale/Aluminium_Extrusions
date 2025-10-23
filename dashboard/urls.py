from django.urls import path
from .views import DashboardView, DieProductionDataView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("dashboard/die/<str:die_no>/production/", DieProductionDataView.as_view(), name="die_production_data"),
]