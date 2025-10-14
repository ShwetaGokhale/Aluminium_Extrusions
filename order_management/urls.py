# urls.py
from django.urls import path
from .views import *

from django.urls import path
from .views import *

urlpatterns = [
    #_______________Customer Requisition________________
    # List View
    path("requisitions/",RequisitionListView.as_view(),name="requisition_list"),
    # Form View (Create)
    path("requisitions/form/",RequisitionFormView.as_view(),name="requisition_form"),
    # Edit View
    path("requisitions/edit/<int:pk>/",RequisitionEditView.as_view(),name="requisition_edit"),
    # API Endpoints
    path("api/requisitions/",RequisitionAPI.as_view(),name="requisition_api"),
    path("api/requisitions/<int:pk>/",RequisitionDetailAPI.as_view(),name="requisition_detail_api"),
    # Delete View
    path("requisitions/delete/<int:pk>/",RequisitionDeleteView.as_view(),name="requisition_delete"),
    # Print View (single)
    path("print-requisition/<int:pk>/", PrintRequisitionView.as_view(), name="print_requisition"),
    # Print View (multiple via query params)
    path("print-requisition/", PrintRequisitionView.as_view(), name="print_requisition_multi"),

    #_______________Work Order________________
    path("workorders/", WorkOrderListView.as_view(), name="work_order_list"),
    path("workorders/add/", WorkOrderView.as_view(), name="work_order"),
    path("api/workorders/", WorkOrderAPI.as_view(), name="work_order_api"),
    path('workorders/edit/<int:pk>/', WorkOrderEditView.as_view(), name='work_order_edit'),
    path('workorders/delete/<int:pk>/', WorkOrderDeleteView.as_view(), name='work_order_delete'),


    #_______________Print Requisition________________
    path('print-requisition/', PrintRequisitionView.as_view(), name='print_requisition_bulk'),
    path('print-requisition/<int:pk>/', PrintRequisitionView.as_view(), name='print_requisition'),


    #_______________Print Work Order________________
    path('print-work-order/', PrintWorkOrderView.as_view(), name='print_work_order_bulk'),
    path("workorder/print/<int:pk>/", PrintWorkOrderView.as_view(), name="print_work_order"),

]

