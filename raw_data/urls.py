from django.urls import path
from .views import LoraReceiveView

urlpatterns = [
    path('lora/receive/', LoraReceiveView.as_view(), name='lora_receive'),
]
#https://demo.extruedge.cloud/api/lora/receive/
