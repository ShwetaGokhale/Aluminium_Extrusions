from django.urls import path
from .views import CurrentProductionView, SensorDetailView

urlpatterns = [
    #_________________Current Production.________________
    path('', CurrentProductionView.as_view(), name='current_production'),
    path('sensor-details/', SensorDetailView.as_view(), name='sensor_details'),
]
