from django.urls import path
from .views import DashboardNewView, PressProductionDataView

urlpatterns = [
    path('', DashboardNewView.as_view(), name='dashboard_new'),
    path('press/<int:press_id>/production/', PressProductionDataView.as_view(), name='press_production_data'),
]