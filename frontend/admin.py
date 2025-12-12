# admin.py
from django.contrib import admin
from django.db.models import Sum, F
from .models import (
    Category, Customer, Product, 
    Sale, Purchase, Debt, DashboardStats
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_count', 'total_value', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'parent', 'description')
        }),
        ('Ko\'rinish', {
            'fields': ('icon', 'color')
        }),
        ('Statistika', {
            'fields': ('product_count', 'total_value')
        }),
    )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'customer_type', 'total_purchases', 'total_spent', 'is_active']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    list_filter = ['customer_type', 'is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_purchase']
    
    fieldsets = (
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'phone', 'email', 'gender', 'birth_date')
        }),
        ('Kompaniya', {
            'fields': ('company', 'tax_id')
        }),
        ('Qo\'shimcha', {
            'fields': ('address', 'notes')
        }),
        ('Status', {
            'fields': ('is_active', 'customer_type')
        }),
        ('Statistika', {
            'fields': ('total_purchases', 'total_spent', 'last_purchase')
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = "Ism Familiya"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'quantity', 'unit', 'sale_price', 'status', 'is_low_stock']
    list_filter = ['category', 'unit', 'status', 'created_at']
    search_fields = ['name', 'sku', 'barcode']
    readonly_fields = ['created_at', 'updated_at', 'total_sold', 'total_revenue']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'sku', 'barcode', 'category', 'brand')
        }),
        ('Narx va miqdor', {
            'fields': ('purchase_price', 'sale_price', 'quantity', 'unit', 'min_quantity')
        }),
        ('Tavsif va rasm', {
            'fields': ('description', 'image')
        }),
        ('Statistika', {
            'fields': ('total_sold', 'total_revenue')
        }),
    )
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = "Kam qolgan"

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'product', 'quantity', 'price', 'total', 'payment_method', 'status', 'sale_date']
    list_filter = ['payment_method', 'status', 'sale_date']
    search_fields = ['customer__first_name', 'customer__last_name', 'product__name', 'invoice_number']
    readonly_fields = ['sale_date', 'updated_at']
    date_hierarchy = 'sale_date'
    
    fieldsets = (
        ('Sotuv ma\'lumotlari', {
            'fields': ('customer', 'product', 'quantity', 'price', 'discount', 'tax')
        }),
        ('To\'lov', {
            'fields': ('payment_method', 'paid_amount')
        }),
        ('Status', {
            'fields': ('status', 'invoice_number', 'notes')
        }),
    )

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'product', 'quantity', 'price', 'total', 'supplier', 'status', 'purchase_date']
    list_filter = ['status', 'purchase_date', 'supplier']
    search_fields = ['product__name', 'supplier__first_name', 'invoice_number']
    readonly_fields = ['purchase_date', 'updated_at']
    date_hierarchy = 'purchase_date'
    
    fieldsets = (
        ('Kirim ma\'lumotlari', {
            'fields': ('product', 'supplier', 'quantity', 'price')
        }),
        ('Qo\'shimcha', {
            'fields': ('invoice_number', 'delivery_date', 'expiry_date', 'notes')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ['customer', 'sale', 'amount', 'paid_amount', 'remaining_amount', 'due_date', 'status', 'is_overdue']
    list_filter = ['status', 'due_date']
    search_fields = ['customer__first_name', 'customer__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Qarz ma\'lumotlari', {
            'fields': ('customer', 'sale', 'amount', 'paid_amount', 'due_date')
        }),
        ('Status', {
            'fields': ('status', 'paid_date', 'notes')
        }),
    )
    
    def remaining_amount(self, obj):
        return obj.remaining_amount
    remaining_amount.short_description = "Qolgan summa"
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = "Muddati o'tgan"

@admin.register(DashboardStats)
class DashboardStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_sales', 'total_purchases', 'total_profit', 'total_customers', 'total_products', 'total_debt']
    readonly_fields = ['date', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    fieldsets = (
        ('Umumiy statistika', {
            'fields': ('date', 'total_sales', 'total_purchases', 'total_profit')
        }),
        ('Mijozlar va mahsulotlar', {
            'fields': ('total_customers', 'new_customers', 'total_products')
        }),
        ('Sotuvlar va kirimlar', {
            'fields': ('sales_count', 'purchase_count')
        }),
        ('Qarzlar', {
            'fields': ('total_debt',)
        }),
    )