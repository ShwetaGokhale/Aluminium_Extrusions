# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    #_______________Die Requisition________________
    # List view
    path('die-requisitions/', DieRequisitionListView.as_view(), name='die_requisition_list'),
    # Form views
    path('die-requisition/', DieRequisitionFormView.as_view(), name='die_requisition'),
    path('die-requisition/edit/<int:pk>/', DieRequisitionEditView.as_view(), name='die_requisition_edit'),
    # API endpoints
    path('api/die-requisitions/', DieRequisitionAPI.as_view(), name='die_requisition_api'),
    path('api/die-requisitions/<int:pk>/', DieRequisitionDetailAPI.as_view(), name='die_requisition_detail_api'),
    # Delete
    path('die-requisition/delete/<int:pk>/', DieRequisitionDeleteView.as_view(), name='die_requisition_delete'),


    # ______________Production Planning________________
    # List view
    path('production-plans/', ProductionPlanListView.as_view(), name='production_plan_list'),
    
    # Form views
    path('production-plan/', ProductionPlanFormView.as_view(), name='production_plan'),
    path('production-plan/edit/<int:pk>/', ProductionPlanEditView.as_view(), name='production_plan_edit'),
    
    # API endpoints
    path('api/production-plans/', ProductionPlanAPI.as_view(), name='production_plan_api'),
    path('api/production-plans/<int:pk>/', ProductionPlanDetailAPI.as_view(), name='production_plan_detail_api'),
    
    # Delete
    path('production-plan/delete/<int:pk>/', ProductionPlanDeleteView.as_view(), name='production_plan_delete'),
    ]