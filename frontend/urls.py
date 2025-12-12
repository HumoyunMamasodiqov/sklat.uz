from django.urls import path
from . import views

urlpatterns = [
    # =============== AUTHENTICATION ===============
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # =============== MAIN PAGES ===============
    path('', views.home, name='home'),
    path('mahsulotlar/', views.mahsulotlar, name='mahsulotlar'),
    path('mijozlar/', views.mijozlar, name='mijozlar'),
    path('analitika/', views.analitika, name='analitika'),
    path('sozlamalar/', views.sozlamalar, name='sozlamalar'),
    
    # =============== PRODUCT OPERATIONS ===============
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('sell-product/', views.sell_product, name='sell_product'),
    
    # =============== CUSTOMER OPERATIONS ===============
    path('add-customer/', views.add_customer, name='add_customer'),
    path('edit-customer/<int:customer_id>/', views.edit_customer, name='edit_customer'),
    path('delete-customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),
    path('customer/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    
    # =============== API ENDPOINTS ===============
    path('api/sales-data/', views.api_sales_data, name='api_sales_data'),
    path('api/sales-chart/', views.api_sales_chart, name='api_sales_chart'),
    path('api/save-language/', views.save_language, name='save_language'),
    path('api/export-report/', views.export_report, name='export_report'),
    
    # =============== TEST PAGES (Ishonch uchun) ===============

]