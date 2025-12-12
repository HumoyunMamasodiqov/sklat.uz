# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F, Q, Avg, Max
from django.utils import timezone
from datetime import datetime, timedelta
import json
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.core.paginator import Paginator
from .models import *

# =============== TEST VIEWS ===============
def test_view(request):
    """Test sahifasi"""
    return HttpResponse("""
    <html>
    <head><title>Test - Sklat.uz</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>✅ Sklat.uz - Test sahifasi</h1>
        <p>Django tizimi ishlayapti!</p>
        <hr>
        <p><strong>URL Testlar:</strong></p>
        <ul>
            <li><a href="/">Bosh sahifa</a></li>
            <li><a href="/login/">Kirish sahifasi</a></li>
            <li><a href="/admin/">Admin panel</a></li>
            <li><a href="/mahsulotlar/">Mahsulotlar</a></li>
            <li><a href="/mijozlar/">Mijozlar</a></li>
            <li><a href="/analitika/">Analitika</a></li>
            <li><a href="/sozlamalar/">Sozlamalar</a></li>
            <li><a href="/add-product/">Mahsulot qo'shish</a></li>
            <li><a href="/sell-product/">Sotuv qilish</a></li>
        </ul>
        <hr>
        <p><strong>Test login:</strong> admin | <strong>Parol:</strong> 123</p>
    </body>
    </html>
    """)

def simple_home(request):
    """Oddiy bosh sahifa"""
    return HttpResponse("""
    <html>
    <head><title>Sklat.uz</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>🏪 Sklat.uz - Do'kon boshqaruv tizimi</h1>
        <p>Tizim ishlayapti!</p>
        <a href="/login/">🔑 Kirish</a> | 
        <a href="/admin/">⚙️ Admin panel</a> | 
        <a href="/test/">🧪 Test sahifa</a>
    </body>
    </html>
    """)

# =============== AUTHENTICATION VIEWS ===============
def login_view(request):
    """Login sahifasi"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Muvaffaqiyatli kirildi!")
            return redirect('home')
        else:
            messages.error(request, "Login yoki parol noto'g'ri!")
    
    return render(request, 'login.html')

def register_view(request):
    """Ro'yxatdan o'tish sahifasi"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Validation
        if password != confirm_password:
            messages.error(request, "Parollar mos kelmadi!")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Bu foydalanuvchi nomi band!")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Bu email band!")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
            return redirect('login')
    
    return render(request, 'register.html')

def logout_view(request):
    """Chiqish"""
    logout(request)
    messages.success(request, "Muvaffaqiyatli chiqildi!")
    return redirect('login')

# =============== MAIN VIEWS ===============
@login_required(login_url='/login/')
def home(request):
    """Bosh sahifa"""
    try:
        # Bugungi sotuvlar
        today = timezone.now().date()
        sales_today = Sale.objects.filter(sale_date__date=today).aggregate(total=Sum('total'))
        total_sales_today = sales_today['total'] or 0
        
        # Jami mahsulotlar
        total_products = Product.objects.count()
        
        # Jami qarz
        total_debt = Debt.objects.filter(status__in=['pending', 'partially_paid', 'overdue']).aggregate(
            total=Sum(F('amount') - F('paid_amount')))
        total_debt_amount = total_debt['total'] or 0
        
        # Jami foyda (bugungi)
        profit_today = Sale.objects.filter(sale_date__date=today).aggregate(
            total_profit=Sum((F('price') - F('product__purchase_price')) * F('quantity'))
        )
        total_profit = profit_today['total_profit'] or 0
        
        # Eng ko'p sotiladigan 5 ta mahsulot
        top_products = Product.objects.annotate(
            total_sold=Sum('sale__quantity')
        ).order_by('-total_sold')[:5]
        
        # Yangi sotuvlar
        recent_sales = Sale.objects.select_related('customer', 'product').order_by('-sale_date')[:5]
        
        # Kam qolgan mahsulotlar
        low_stock_products = Product.objects.filter(quantity__lte=F('min_quantity'))[:5]
        
        # Kategoriyalar ro'yxati
        categories = Category.objects.all()[:4]
        
        # Quick Actions
        quick_actions = [
            {'name': 'Kirim', 'icon': 'inbox-archive-line', 'color': 'green', 'url': '/add-product/'},
            {'name': 'Sotuv', 'icon': 'shopping-cart-line', 'color': 'red', 'url': '/sell-product/'},
            {'name': 'Analitika', 'icon': 'bar-chart-line', 'color': 'blue', 'url': '/analitika/'},
            {'name': 'Hisobot', 'icon': 'file-chart-line', 'color': 'purple', 'url': '/analitika/?report=detailed'},
        ]
        
        context = {
            'total_sales_today': f"{total_sales_today:,.0f}",
            'total_products': total_products,
            'total_debt': f"{total_debt_amount:,.0f}",
            'total_profit': f"{total_profit:,.0f}",
            'top_products': top_products,
            'recent_sales': recent_sales,
            'low_stock_products': low_stock_products,
            'categories': categories,
            'quick_actions': quick_actions,
            'user': request.user,
        }
        
        return render(request, 'home.html', context)
        
    except Exception as e:
        # Agar database bo'lmasa yoki xato bo'lsa
        context = {
            'total_sales_today': "0",
            'total_products': "0",
            'total_debt': "0",
            'total_profit': "0",
            'top_products': [],
            'recent_sales': [],
            'low_stock_products': [],
            'categories': [],
            'quick_actions': [
                {'name': 'Kirim', 'icon': 'inbox-archive-line', 'color': 'green', 'url': '#'},
                {'name': 'Sotuv', 'icon': 'shopping-cart-line', 'color': 'red', 'url': '#'},
                {'name': 'Analitika', 'icon': 'bar-chart-line', 'color': 'blue', 'url': '#'},
                {'name': 'Hisobot', 'icon': 'file-chart-line', 'color': 'purple', 'url': '#'},
            ],
            'user': request.user,
        }
        return render(request, 'home.html', context)

@login_required(login_url='/login/')
def mahsulotlar(request):
    """Mahsulotlar ro'yxati"""
    # Kategoriya bo'yicha filtr
    category_filter = request.GET.get('category', 'all')
    search_query = request.GET.get('q', '')
    
    products = Product.objects.select_related('category').all()
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query)
        )
    
    if category_filter != 'all':
        products = products.filter(category__name=category_filter)
    
    # Pagination
    paginator = Paginator(products, 20)  # Sahifada 20 ta mahsulot
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Kategoriyalar ro'yxati
    categories = Category.objects.all()
    
    # Statistika
    total_products = products.count()
    low_stock_count = products.filter(quantity__lte=F('min_quantity')).count()
    total_categories = categories.count()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_categories': total_categories,
        'current_category': category_filter,
        'search_query': search_query,
        'user': request.user,
    }
    
    return render(request, 'mahsulotlar.html', context)

@login_required(login_url='/login/')
def mijozlar(request):
    """Mijozlar ro'yxati"""
    search_query = request.GET.get('q', '')
    
    customers = Customer.objects.all()
    
    if search_query:
        customers = customers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Har bir mijoz uchun statistikani hisoblash
    customers_with_stats = []
    for customer in page_obj:
        customer_stats = Sale.objects.filter(customer=customer).aggregate(
            total_purchases=Count('id'),
            total_spent=Sum('total'),
            last_purchase=Max('sale_date')
        )
        
        customers_with_stats.append({
            'customer': customer,
            'total_purchases': customer_stats['total_purchases'] or 0,
            'total_spent': customer_stats['total_spent'] or 0,
            'last_purchase': customer_stats['last_purchase']
        })
    
    # Umumiy statistika
    total_customers = customers.count()
    
    active_customers = customers.annotate(
        purchase_count=Count('sale')
    ).filter(purchase_count__gt=0).count()
    
    new_customers_this_month = customers.filter(
        created_at__month=timezone.now().month,
        created_at__year=timezone.now().year
    ).count()
    
    avg_purchase = Sale.objects.aggregate(
        avg_total=Avg('total')
    )
    
    context = {
        'customers_with_stats': customers_with_stats,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'new_customers_this_month': new_customers_this_month,
        'avg_purchase': avg_purchase['avg_total'] or 0,
        'search_query': search_query,
        'page_obj': page_obj,
        'user': request.user,
    }
    
    return render(request, 'mijozlar.html', context)

@login_required(login_url='/login/')
def analitika(request):
    """Analitika sahifasi"""
    # Vaqt oralig'ini aniqlash
    period = request.GET.get('period', 'day')
    
    if period == 'day':
        # Kunlik ma'lumotlar (soatlar bo'yicha)
        start_date = timezone.now().date()
        labels = [f"{i}:00" for i in range(6, 22, 2)]
        
        # Soatlar bo'yicha guruhlash
        sales_data = []
        for hour in range(6, 22, 2):
            hour_start = timezone.make_aware(datetime(start_date.year, start_date.month, start_date.day, hour))
            hour_end = hour_start + timedelta(hours=2)
            hour_sales = Sale.objects.filter(
                sale_date__gte=hour_start,
                sale_date__lt=hour_end
            ).aggregate(total=Sum('total'))
            sales_data.append(float(hour_sales['total'] or 0))
    
    elif period == 'week':
        # Haftalik ma'lumotlar
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)
        labels = ['Dush', 'Sesh', 'Chor', 'Pay', 'Jum', 'Shan', 'Yak']
        
        # Kunlar bo'yicha guruhlash
        sales_data = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            day_sales = Sale.objects.filter(sale_date__date=day).aggregate(total=Sum('total'))
            sales_data.append(float(day_sales['total'] or 0))
    
    elif period == 'month':
        # Oylik ma'lumotlar (haftalar bo'yicha)
        start_date = timezone.now().date().replace(day=1)
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
        
        weeks = []
        current_date = start_date
        while current_date <= end_date:
            week_end = current_date + timedelta(days=6)
            if week_end > end_date:
                week_end = end_date
            weeks.append((current_date, week_end))
            current_date = week_end + timedelta(days=1)
        
        labels = [f"{i+1}-hafta" for i in range(len(weeks))]
        sales_data = []
        
        for week_start, week_end in weeks:
            week_sales = Sale.objects.filter(
                sale_date__date__gte=week_start,
                sale_date__date__lte=week_end
            ).aggregate(total=Sum('total'))
            sales_data.append(float(week_sales['total'] or 0))
    
    else:  # year
        # Yillik ma'lumotlar (oylar bo'yicha)
        current_year = timezone.now().year
        labels = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn', 'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek']
        sales_data = []
        
        for month in range(1, 13):
            month_sales = Sale.objects.filter(
                sale_date__year=current_year,
                sale_date__month=month
            ).aggregate(total=Sum('total'))
            sales_data.append(float(month_sales['total'] or 0))
    
    # Kategoriyalar bo'yicha sotuvlar
    category_data = []
    categories = Category.objects.all()
    
    for category in categories:
        category_sales = Sale.objects.filter(product__category=category).aggregate(
            total_amount=Sum('total'),
            total_quantity=Sum('quantity')
        )
        category_data.append({
            'name': category.name,
            'amount': float(category_sales['total_amount'] or 0),
            'quantity': float(category_sales['total_quantity'] or 0)
        })
    
    # Eng ko'p sotiladigan mahsulotlar
    top_products = Product.objects.annotate(
        total_sold=Sum('sale__quantity'),
        total_revenue=Sum('sale__total')
    ).order_by('-total_sold')[:5]
    
    # Umumiy statistika
    total_sales_month = Sale.objects.filter(
        sale_date__month=timezone.now().month
    ).aggregate(total=Sum('total'))
    
    total_customers = Customer.objects.count()
    
    active_customers = Customer.objects.annotate(
        purchase_count=Count('sale')
    ).filter(purchase_count__gt=0).count()
    
    # O'rtacha xarid
    avg_purchase = Sale.objects.aggregate(
        avg_total=Avg('total')
    )
    
    context = {
        'period': period,
        'sales_labels': json.dumps(labels),
        'sales_data': json.dumps(sales_data),
        'category_data': json.dumps(category_data),
        'top_products': top_products,
        'total_sales_month': total_sales_month['total'] or 0,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'avg_purchase': avg_purchase['avg_total'] or 0,
        'user': request.user,
    }
    
    return render(request, 'analitika.html', context)

@login_required(login_url='/login/')
def sozlamalar(request):
    """Sozlamalar sahifasi"""
    user = request.user
    
    if request.method == 'POST':
        # AJAX so'rovlarni qayta ishlash
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if 'update_profile' in request.POST:
                user.first_name = request.POST.get('first_name', user.first_name)
                user.last_name = request.POST.get('last_name', user.last_name)
                user.email = request.POST.get('email', user.email)
                user.save()
                return JsonResponse({
                    'success': True,
                    'message': "Profil ma'lumotlari yangilandi!"
                })
            
            elif 'change_password' in request.POST:
                old_password = request.POST.get('old_password')
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                
                if not user.check_password(old_password):
                    return JsonResponse({
                        'success': False,
                        'message': "Eski parol noto'g'ri!"
                    })
                
                if new_password != confirm_password:
                    return JsonResponse({
                        'success': False,
                        'message': "Yangi parollar mos kelmadi!"
                    })
                
                if len(new_password) < 8:
                    return JsonResponse({
                        'success': False,
                        'message': "Parol kamida 8 ta belgidan iborat bo'lishi kerak!"
                    })
                
                user.set_password(new_password)
                user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': "Parol muvaffaqiyatli yangilandi!"
                })
        
        # Oddiy POST so'rovlarni qayta ishlash
        if 'update_profile' in request.POST:
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()
            messages.success(request, "Profil ma'lumotlari yangilandi!")
            return redirect('sozlamalar')
        
        elif 'change_password' in request.POST:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if user.check_password(old_password):
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, "Parol muvaffaqiyatli yangilandi!")
                    return redirect('login')
                else:
                    messages.error(request, "Yangi parollar mos kelmadi!")
            else:
                messages.error(request, "Eski parol noto'g'ri!")
    
    context = {
        'user': user,
    }
    
    return render(request, 'sozlamalar.html', context)

# =============== PRODUCT OPERATIONS ===============
@login_required(login_url='/login/')
def add_product(request):
    """Mahsulot qo'shish"""
    if request.method == 'POST':
        name = request.POST.get('name')
        sku = request.POST.get('sku')
        category_id = request.POST.get('category')
        purchase_price = request.POST.get('purchase_price')
        sale_price = request.POST.get('sale_price')
        quantity = request.POST.get('quantity')
        unit = request.POST.get('unit')
        min_quantity = request.POST.get('min_quantity', 5)
        description = request.POST.get('description', '')
        
        # Validation
        if not all([name, sku, category_id, purchase_price, sale_price, quantity, unit]):
            messages.error(request, "Barcha majburiy maydonlarni to'ldiring!")
            categories = Category.objects.all()
            return render(request, 'add_product.html', {'categories': categories})
        
        try:
            # Check if SKU already exists
            if Product.objects.filter(sku=sku).exists():
                messages.error(request, "Bu SKU kodi bilan mahsulot allaqachon mavjud!")
                categories = Category.objects.all()
                return render(request, 'add_product.html', {'categories': categories})
            
            category = get_object_or_404(Category, id=category_id)
            
            product = Product(
                name=name,
                sku=sku,
                category=category,
                purchase_price=float(purchase_price),
                sale_price=float(sale_price),
                quantity=float(quantity),
                unit=unit,
                min_quantity=float(min_quantity),
                description=description
            )
            
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            product.save()
            messages.success(request, f"'{name}' mahsuloti muvaffaqiyatli qo'shildi!")
            return redirect('mahsulotlar')
            
        except Category.DoesNotExist:
            messages.error(request, "Kategoriya topilmadi!")
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'user': request.user,
    }
    return render(request, 'add_product.html', context)

@login_required(login_url='/login/')
def edit_product(request, product_id):
    """Mahsulotni tahrirlash"""
    try:
        product = get_object_or_404(Product, id=product_id)
        
        if request.method == 'POST':
            product.name = request.POST.get('name', product.name)
            product.sku = request.POST.get('sku', product.sku)
            product.category_id = request.POST.get('category', product.category_id)
            product.purchase_price = request.POST.get('purchase_price', product.purchase_price)
            product.sale_price = request.POST.get('sale_price', product.sale_price)
            product.quantity = request.POST.get('quantity', product.quantity)
            product.unit = request.POST.get('unit', product.unit)
            product.min_quantity = request.POST.get('min_quantity', product.min_quantity)
            
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            product.save()
            messages.success(request, "Mahsulot muvaffaqiyatli yangilandi!")
            return redirect('mahsulotlar')
        
        categories = Category.objects.all()
        context = {
            'product': product,
            'categories': categories,
            'user': request.user,
        }
        return render(request, 'edit_product.html', context)
        
    except Product.DoesNotExist:
        messages.error(request, "Mahsulot topilmadi!")
        return redirect('mahsulotlar')

@login_required(login_url='/login/')
def delete_product(request, product_id):
    """Mahsulotni o'chirish"""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            product_name = product.name
            product.delete()
            messages.success(request, f"'{product_name}' mahsuloti muvaffaqiyatli o'chirildi!")
        except Product.DoesNotExist:
            messages.error(request, "Mahsulot topilmadi!")
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    return redirect('mahsulotlar')

@login_required(login_url='/login/')
def product_detail(request, product_id):
    """Mahsulot tafsilotlari"""
    try:
        product = get_object_or_404(Product, id=product_id)
        
        # Mahsulot sotuvlari
        sales = Sale.objects.filter(product=product).order_by('-sale_date')[:10]
        
        # Mahsulot kirimlari
        purchases = Purchase.objects.filter(product=product).order_by('-purchase_date')[:10]
        
        context = {
            'product': product,
            'sales': sales,
            'purchases': purchases,
            'user': request.user,
        }
        return render(request, 'product_detail.html', context)
        
    except Product.DoesNotExist:
        messages.error(request, "Mahsulot topilmadi!")
        return redirect('mahsulotlar')

@login_required(login_url='/login/')
def sell_product(request):
    """Mahsulot sotish"""
    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = float(request.POST.get('quantity', 0))
        price = float(request.POST.get('price', 0))
        customer_id = request.POST.get('customer')
        payment_method = request.POST.get('payment_method', 'cash')
        
        try:
            product = get_object_or_404(Product, id=product_id)
            customer = get_object_or_404(Customer, id=customer_id) if customer_id else None
            
            if product.quantity < quantity:
                messages.error(request, "Mahsulot yetarli emas!")
                return redirect('mahsulotlar')
            
            total = quantity * price
            
            # Mahsulot miqdorini kamaytirish
            product.quantity -= quantity
            product.save()
            
            sale = Sale.objects.create(
                product=product,
                quantity=quantity,
                price=price,
                total=total,
                customer=customer,
                payment_method=payment_method,
                created_by=request.user
            )
            
            # Agar nasiya bo'lsa, qarz yaratish
            if payment_method == 'credit':
                Debt.objects.create(
                    customer=customer,
                    sale=sale,
                    amount=total,
                    due_date=timezone.now().date() + timedelta(days=30),
                    status='pending'
                )
            
            messages.success(request, f"Sotuv muvaffaqiyatli amalga oshirildi! Jami: {total:,.0f} so'm")
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
            return redirect('sell_product')
    
    products = Product.objects.filter(quantity__gt=0)
    customers = Customer.objects.all()
    return render(request, 'sell_product.html', {
        'products': products,
        'customers': customers,
        'user': request.user,
    })

# =============== CUSTOMER OPERATIONS ===============
@login_required(login_url='/login/')
def add_customer(request):
    """Mijoz qo'shish"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        note = request.POST.get('note')
        
        try:
            # Telefon raqami tekshirish
            if Customer.objects.filter(phone=phone).exists():
                messages.error(request, "Bu telefon raqamli mijoz allaqachon mavjud!")
            else:
                customer = Customer.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    address=address,
                    note=note
                )
                messages.success(request, "Mijoz muvaffaqiyatli qo'shildi!")
                return redirect('mijozlar')
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    context = {
        'user': request.user,
    }
    return render(request, 'add_customer.html', context)

@login_required(login_url='/login/')
def edit_customer(request, customer_id):
    """Mijozni tahrirlash"""
    try:
        customer = get_object_or_404(Customer, id=customer_id)
        
        if request.method == 'POST':
            customer.first_name = request.POST.get('first_name', customer.first_name)
            customer.last_name = request.POST.get('last_name', customer.last_name)
            customer.phone = request.POST.get('phone', customer.phone)
            customer.email = request.POST.get('email', customer.email)
            customer.address = request.POST.get('address', customer.address)
            customer.note = request.POST.get('note', customer.note)
            
            customer.save()
            messages.success(request, "Mijoz ma'lumotlari yangilandi!")
            return redirect('customer_detail', customer_id=customer.id)
        
        context = {
            'customer': customer,
            'user': request.user,
        }
        return render(request, 'edit_customer.html', context)
        
    except Customer.DoesNotExist:
        messages.error(request, "Mijoz topilmadi!")
        return redirect('mijozlar')

@login_required(login_url='/login/')
def delete_customer(request, customer_id):
    """Mijozni o'chirish"""
    if request.method == 'POST':
        try:
            customer = get_object_or_404(Customer, id=customer_id)
            customer_name = customer.full_name
            customer.delete()
            messages.success(request, f"'{customer_name}' mijoz muvaffaqiyatli o'chirildi!")
        except Customer.DoesNotExist:
            messages.error(request, "Mijoz topilmadi!")
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    return redirect('mijozlar')

@login_required(login_url='/login/')
def customer_detail(request, customer_id):
    """Mijoz tafsilotlari"""
    try:
        customer = get_object_or_404(Customer, id=customer_id)
        
        # Mijozning sotuvlari
        sales = Sale.objects.filter(customer=customer).order_by('-sale_date')
        
        # Mijoz statistikasi
        total_sales = sales.count()
        total_spent = sales.aggregate(total=Sum('total'))['total'] or 0
        avg_sale = sales.aggregate(avg=Avg('total'))['avg'] or 0
        
        # Oxirgi xaridlar
        recent_sales = sales[:10]
        
        # Nasiya qarzlari
        debts = Debt.objects.filter(customer=customer, status__in=['pending', 'partially_paid'])
        total_debt = debts.aggregate(total=Sum(F('amount') - F('paid_amount')))['total'] or 0
        
        context = {
            'customer': customer,
            'sales': sales,
            'recent_sales': recent_sales,
            'total_sales': total_sales,
            'total_spent': total_spent,
            'avg_sale': avg_sale,
            'total_debt': total_debt,
            'debts': debts,
            'user': request.user,
        }
        return render(request, 'customer_detail.html', context)
        
    except Customer.DoesNotExist:
        messages.error(request, "Mijoz topilmadi!")
        return redirect('mijozlar')

# =============== PURCHASE OPERATIONS ===============
@login_required(login_url='/login/')
def add_purchase(request):
    """Kirim (purchase) qo'shish"""
    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = float(request.POST.get('quantity', 0))
        price = float(request.POST.get('price', 0))
        supplier = request.POST.get('supplier')
        
        try:
            product = get_object_or_404(Product, id=product_id)
            total = quantity * price
            
            # Mahsulot miqdorini oshirish
            product.quantity += quantity
            product.save()
            
            purchase = Purchase.objects.create(
                product=product,
                quantity=quantity,
                price=price,
                total=total,
                supplier=supplier,
                created_by=request.user
            )
            
            messages.success(request, f"Kirim muvaffaqiyatli qo'shildi! Jami: {total:,.0f} so'm")
            return redirect('mahsulotlar')
            
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    products = Product.objects.all()
    return render(request, 'add_purchase.html', {
        'products': products,
        'user': request.user,
    })

# =============== DEBT OPERATIONS ===============
@login_required(login_url='/login/')
def pay_debt(request, debt_id):
    """Qarz to'lash"""
    if request.method == 'POST':
        try:
            debt = get_object_or_404(Debt, id=debt_id)
            amount = float(request.POST.get('amount', 0))
            
            if amount <= 0:
                messages.error(request, "To'lov summasi noto'g'ri!")
                return redirect('customer_detail', customer_id=debt.customer.id)
            
            debt.paid_amount += amount
            
            # Agar to'liq to'langan bo'lsa
            if debt.paid_amount >= debt.amount:
                debt.status = 'paid'
            else:
                debt.status = 'partially_paid'
            
            debt.save()
            
            messages.success(request, f"Qarz to'lovi qabul qilindi: {amount:,.0f} so'm")
            return redirect('customer_detail', customer_id=debt.customer.id)
            
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    return redirect('mijozlar')

# =============== CATEGORY OPERATIONS ===============
@login_required(login_url='/login/')
def add_category(request):
    """Kategoriya qo'shish"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        parent_id = request.POST.get('parent', None)
        icon = request.POST.get('icon', 'ri-folder-line')
        color = request.POST.get('color', '#3B82F6')
        
        try:
            parent = None
            if parent_id:
                parent = Category.objects.get(id=parent_id)
            
            category = Category.objects.create(
                name=name,
                description=description,
                parent=parent,
                icon=icon,
                color=color,
                user=request.user
            )
            
            messages.success(request, f"'{name}' kategoriyasi muvaffaqiyatli qo'shildi!")
            return redirect('mahsulotlar')
            
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'user': request.user,
    }
    return render(request, 'add_category.html', context)

@login_required(login_url='/login/')
def edit_category(request, category_id):
    """Kategoriyani tahrirlash"""
    try:
        category = get_object_or_404(Category, id=category_id)
        
        if request.method == 'POST':
            category.name = request.POST.get('name', category.name)
            category.description = request.POST.get('description', category.description)
            
            parent_id = request.POST.get('parent')
            if parent_id:
                category.parent = Category.objects.get(id=parent_id)
            else:
                category.parent = None
            
            category.icon = request.POST.get('icon', category.icon)
            category.color = request.POST.get('color', category.color)
            
            category.save()
            messages.success(request, "Kategoriya muvaffaqiyatli yangilandi!")
            return redirect('mahsulotlar')
        
        categories = Category.objects.exclude(id=category_id)
        context = {
            'category': category,
            'categories': categories,
            'user': request.user,
        }
        return render(request, 'edit_category.html', context)
        
    except Category.DoesNotExist:
        messages.error(request, "Kategoriya topilmadi!")
        return redirect('mahsulotlar')

@login_required(login_url='/login/')
def delete_category(request, category_id):
    """Kategoriyani o'chirish"""
    if request.method == 'POST':
        try:
            category = get_object_or_404(Category, id=category_id)
            category_name = category.name
            
            # Kategoriyada mahsulotlar bormi?
            if category.products.exists():
                messages.error(request, f"'{category_name}' kategoriyasida mahsulotlar bor. Avval mahsulotlarni boshqa kategoriyaga o'tkazish kerak!")
                return redirect('mahsulotlar')
            
            category.delete()
            messages.success(request, f"'{category_name}' kategoriyasi muvaffaqiyatli o'chirildi!")
        except Category.DoesNotExist:
            messages.error(request, "Kategoriya topilmadi!")
        except Exception as e:
            messages.error(request, f"Xatolik: {str(e)}")
    
    return redirect('mahsulotlar')

# =============== API VIEWS ===============
@login_required(login_url='/login/')
def api_sales_data(request):
    """API: Sotuv ma'lumotlari"""
    period = request.GET.get('period', 'day')
    
    if period == 'day':
        # Kunlik ma'lumotlar
        today = timezone.now().date()
        sales = Sale.objects.filter(sale_date__date=today)
        data = list(sales.values('sale_date__hour').annotate(total=Sum('total')).order_by('sale_date__hour'))
    elif period == 'week':
        # Haftalik ma'lumotlar
        week_ago = timezone.now().date() - timedelta(days=7)
        data = []
        for i in range(7):
            day = week_ago + timedelta(days=i)
            day_sales = Sale.objects.filter(sale_date__date=day).aggregate(total=Sum('total'))
            data.append({
                'date': day.strftime('%Y-%m-%d'),
                'total': float(day_sales['total'] or 0)
            })
    else:
        data = []
    
    return JsonResponse({'data': data})

@login_required(login_url='/login/')
def api_sales_chart(request):
    """API: Sotuv grafigi ma'lumotlari"""
    period = request.GET.get('period', 'day')
    
    if period == 'day':
        # Kunlik ma'lumotlar
        today = timezone.now().date()
        hours = range(6, 22, 2)
        data = []
        
        for hour in hours:
            hour_start = timezone.make_aware(datetime(today.year, today.month, today.day, hour))
            hour_end = hour_start + timedelta(hours=2)
            hour_sales = Sale.objects.filter(
                sale_date__gte=hour_start,
                sale_date__lt=hour_end
            ).aggregate(total=Sum('total'))
            
            data.append({
                'hour': f"{hour}:00",
                'amount': float(hour_sales['total'] or 0)
            })
        
        return JsonResponse({'data': data})
    
    elif period == 'week':
        # Haftalik ma'lumotlar
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
        
        data = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            day_sales = Sale.objects.filter(sale_date__date=day).aggregate(total=Sum('total'))
            
            data.append({
                'date': day.strftime('%Y-%m-%d'),
                'day': ['Dush', 'Sesh', 'Chor', 'Pay', 'Jum', 'Shan', 'Yak'][i],
                'amount': float(day_sales['total'] or 0)
            })
        
        return JsonResponse({'data': data})
    
    return JsonResponse({'data': []})

@login_required(login_url='/login/')
def api_get_products(request):
    """API: Mahsulotlar ro'yxati (AJAX)"""
    search = request.GET.get('search', '')
    
    products = Product.objects.filter(quantity__gt=0)
    
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search)
        )[:10]
    
    product_list = []
    for product in products:
        product_list.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'price': str(product.sale_price),
            'quantity': str(product.quantity),
            'unit': product.unit
        })
    
    return JsonResponse({'products': product_list})

@login_required(login_url='/login/')
def api_get_customers(request):
    """API: Mijozlar ro'yxati (AJAX)"""
    search = request.GET.get('search', '')
    
    customers = Customer.objects.all()
    
    if search:
        customers = customers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone__icontains=search)
        )[:10]
    
    customer_list = []
    for customer in customers:
        customer_list.append({
            'id': customer.id,
            'name': customer.full_name,
            'phone': customer.phone
        })
    
    return JsonResponse({'customers': customer_list})

@login_required(login_url='/login/')
def save_language(request):
    """API: Til sozlamalarini saqlash"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            language = data.get('language', 'uz')
            
            # Bu yerda foydalanuvchi til sozlamalarini saqlashingiz mumkin
            # Masalan: user.profile.language = language
            # user.profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Til sozlamalari saqlandi!'
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Noto\'g\'ri JSON format!'})
    
    return JsonResponse({'success': False, 'message': 'Noto\'g\'ri so\'rov!'})

# =============== REPORT VIEWS ===============
@login_required(login_url='/login/')
def export_report(request):
    """Hisobot yuklab olish"""
    format_type = request.GET.get('format', 'pdf')
    report_type = request.GET.get('type', 'sales')
    period = request.GET.get('period', 'month')
    
    try:
        # Ma'lumotlarni olish
        if report_type == 'sales':
            # Sotuv ma'lumotlarini olish
            if period == 'day':
                today = timezone.now().date()
                sales = Sale.objects.filter(sale_date__date=today)
            elif period == 'week':
                week_ago = timezone.now().date() - timedelta(days=7)
                sales = Sale.objects.filter(sale_date__date__gte=week_ago)
            elif period == 'month':
                month_start = timezone.now().date().replace(day=1)
                sales = Sale.objects.filter(sale_date__date__gte=month_start)
            else:  # year
                year_start = timezone.now().date().replace(month=1, day=1)
                sales = Sale.objects.filter(sale_date__date__gte=year_start)
            
            # Ma'lumotlar yo'q bo'lsa
            if not sales.exists():
                messages.error(request, "Hisobot uchun ma'lumot topilmadi!")
                return redirect('analitika')
        
        if format_type == 'pdf':
            # PDF yaratish
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="report_{period}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
            
            p = canvas.Canvas(response, pagesize=letter)
            p.setTitle(f"Sotuv hisoboti - {period}")
            
            # Sarlavha
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, 750, f"Sklat.uz - Sotuv hisoboti")
            p.setFont("Helvetica", 12)
            p.drawString(100, 730, f"Davr: {period}")
            p.drawString(100, 710, f"Yaratilgan sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Ma'lumotlar
            total_sales = sales.aggregate(total=Sum('total'))['total'] or 0
            p.drawString(100, 680, f"Jami sotuv: {total_sales:,.0f} so'm")
            
            # Grafik qo'shish mumkin...
            
            p.showPage()
            p.save()
            
            return response
        
        elif format_type == 'excel':
            # Excel yaratish
            data = []
            for sale in sales[:100]:  # Faqat 100 ta yozuv
                data.append({
                    'ID': sale.id,
                    'Mahsulot': sale.product.name,
                    'Miqdor': sale.quantity,
                    'Narx': sale.price,
                    'Jami': sale.total,
                    'Sana': sale.sale_date.strftime('%Y-%m-%d %H:%M'),
                    'Mijoz': sale.customer.full_name if sale.customer else 'Noma\'lum'
                })
            
            df = pd.DataFrame(data)
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Sotuvlar', index=False)
            
            output.seek(0)
            
            response = HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="report_{period}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
            
            return response
        
        else:
            messages.error(request, "Noto'g'ri format tanlandi!")
            return redirect('analitika')
            
    except Exception as e:
        messages.error(request, f"Hisobot yaratishda xatolik: {str(e)}")
        return redirect('analitika')

# =============== URL MAPPING ===============
# Quyidagi urlpatterns ro'yxatini urls.py fayliga qo'shishingiz kerak:

"""
from django.urls import path
from . import views

urlpatterns = [
    # Test URL'lar
    path('test/', views.test_view, name='test'),
    path('simple-home/', views.simple_home, name='simple_home'),
    
    # Autentifikatsiya
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Asosiy sahifalar
    path('', views.home, name='home'),
    path('mahsulotlar/', views.mahsulotlar, name='mahsulotlar'),
    path('mijozlar/', views.mijozlar, name='mijozlar'),
    path('analitika/', views.analitika, name='analitika'),
    path('sozlamalar/', views.sozlamalar, name='sozlamalar'),
    
    # Mahsulot operatsiyalari
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product-detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('sell-product/', views.sell_product, name='sell_product'),
    
    # Mijoz operatsiyalari
    path('add-customer/', views.add_customer, name='add_customer'),
    path('edit-customer/<int:customer_id>/', views.edit_customer, name='edit_customer'),
    path('delete-customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),
    path('customer-detail/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    
    # Kirim operatsiyalari
    path('add-purchase/', views.add_purchase, name='add_purchase'),
    
    # Qarz operatsiyalari
    path('pay-debt/<int:debt_id>/', views.pay_debt, name='pay_debt'),
    
    # Kategoriya operatsiyalari
    path('add-category/', views.add_category, name='add_category'),
    path('edit-category/<uuid:category_id>/', views.edit_category, name='edit_category'),
    path('delete-category/<uuid:category_id>/', views.delete_category, name='delete_category'),
    
    # API endpoint'lar
    path('api/sales-data/', views.api_sales_data, name='api_sales_data'),
    path('api/sales-chart/', views.api_sales_chart, name='api_sales_chart'),
    path('api/get-products/', views.api_get_products, name='api_get_products'),
    path('api/get-customers/', views.api_get_customers, name='api_get_customers'),
    path('api/save-language/', views.save_language, name='save_language'),
    
    # Hisobotlar
    path('export-report/', views.export_report, name='export_report'),
]
"""