# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    #_______________Die Master________________
    # Form views
    path('die/', DieFormView.as_view(), name='die_create'),
    path('die/edit/<int:die_id>/', DieEditView.as_view(), name='die_edit'),  
    # API endpoints
    path('api/dies/', DieAPI.as_view(), name='die_api_create'),
    path('api/dies/<int:die_id>/', DieDetailAPI.as_view(), name='die_detail_api'),  
    # List view
    path('dies/', DieListView.as_view(), name='die_list'),

    #_______________Press________________
    path("press/", PressListView.as_view(), name="press"), # ✅ renamed for consistency
    path("presses/", PressListView.as_view(), name="press-list"),
    path("api/presses/", PressAPI.as_view(), name="presses-api"),
    path("api/presses/<str:press_id>/", PressDetailAPI.as_view(), name="press-detail-api"),

    #_______________Alloy Harness________________
    # List view
    path('alloys/', AlloyListView.as_view(), name='alloy_list'),
    
    # Form views
    path('alloy/', AlloyFormView.as_view(), name='alloy_form'),
    path('alloy/edit/<int:pk>/', AlloyEditView.as_view(), name='alloy_edit'),
    
    # API endpoints
    path('api/alloys/', AlloyAPI.as_view(), name='alloy_api'),
    path('api/alloys/<int:pk>/', AlloyDetailAPI.as_view(), name='alloy_detail_api'),
    
    # Delete
    path('alloy/delete/<int:pk>/', AlloyDeleteView.as_view(), name='alloy_delete'),

    #_______________LOT________________
    path("lots/", LotListView.as_view(), name="lot"),  # ✅ renamed for consistency
    path("lots-list/", LotListView.as_view(), name="lot-list"),  
    path("api/lots/", LotAPI.as_view(), name="lots-api"),
    path("api/lots/<int:lot_id>/", LotDetailAPI.as_view(), name="lot-detail-api"),

    #_______________Profile________________
    # Page views
    path("profiles/", ProfileListView.as_view(), name="profile"),   # ✅ renamed for consistency
    path("profiles-list/", ProfileListView.as_view(), name="profile-list"),  
    # API endpoints
    path("api/profiles/", ProfileAPI.as_view(), name="profiles-api"),
    path("api/profiles/<int:profile_id>/", ProfileDetailAPI.as_view(), name="profile-detail-api"),

    #_______________Customer________________
    # List view
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    
    # Form views
    path('customer/', CustomerFormView.as_view(), name='customer'),
    path('customer/edit/<int:pk>/', CustomerEditView.as_view(), name='customer_edit'),
    
    # API endpoints
    path('api/customers/', CustomerAPI.as_view(), name='customer_api'),
    path('api/customers/<int:pk>/', CustomerDetailAPI.as_view(), name='customer_detail_api'),
    
    # Delete
    path('customer/delete/<int:pk>/', CustomerDeleteView.as_view(), name='customer_delete'),



    #_______________Company________________
    # Company form views
    path('company/', CompanyFormView.as_view(), name='company_create'),
    path('company/edit/<int:company_id>/', CompanyEditView.as_view(), name='company_edit'),
    # API endpoints
    path('api/companies/', CompanyAPI.as_view(), name='company_api_create'),
    path('api/companies/<int:company_id>/', CompanyDetailAPI.as_view(), name='company_detail_api'),
    # List view
    path('companies/', CompanyListView.as_view(), name='company_list'),


    #_______________Supplier________________
    # List view
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    
    # Form views
    path('supplier/', SupplierFormView.as_view(), name='supplier'),
    path('supplier/edit/<int:pk>/', SupplierEditView.as_view(), name='supplier_edit'),
    
    # API endpoints
    path('api/suppliers/', SupplierAPI.as_view(), name='supplier_api'),
    path('api/suppliers/<int:pk>/', SupplierDetailAPI.as_view(), name='supplier_detail_api'),
    
    # Delete
    path('supplier/delete/<int:pk>/', SupplierDeleteView.as_view(), name='supplier_delete'),


    #_______________Staff________________
    # List view
    path('staff/', StaffListView.as_view(), name='staff_list'),
    
    # Form views
    path('staff/form/', StaffFormView.as_view(), name='staff_form'),
    path('staff/edit/<int:pk>/', StaffEditView.as_view(), name='staff_edit'),
    
    # API endpoints
    path('api/staff/', StaffAPI.as_view(), name='staff_api'),
    path('api/staff/<int:pk>/', StaffDetailAPI.as_view(), name='staff_detail_api'),
    
    # Delete
    path('staff/delete/<int:pk>/', StaffDeleteView.as_view(), name='staff_delete'),


    #_______________Section________________
    # List view
    path('sections/', SectionListView.as_view(), name='section_list'),
    
    # Form views
    path('section/', SectionFormView.as_view(), name='section_form'),
    path('section/edit/<int:pk>/', SectionEditView.as_view(), name='section_edit'),
    
    # API endpoints
    path('api/sections/', SectionAPI.as_view(), name='section_api'),
    path('api/sections/<int:pk>/', SectionDetailAPI.as_view(), name='section_detail_api'),
    
    # Delete
    path('section/delete/<int:pk>/', SectionDeleteView.as_view(), name='section_delete'),
]