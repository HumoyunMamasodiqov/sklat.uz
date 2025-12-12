# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid

class Category(models.Model):
    """Mahsulot kategoriyalari"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    icon = models.CharField(max_length=50, default="ri-folder-line", verbose_name="Ikonka")
    color = models.CharField(max_length=7, default="#3B82F6", verbose_name="Rang")
    
    # Statistics
    product_count = models.IntegerField(default=0, verbose_name="Mahsulotlar soni")
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Jami qiymati")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Foreign keys
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name="subcategories", verbose_name="Ota kategoriya")

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['name']
        unique_together = ['name', 'user']  # Har bir user uchun nom unique

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Slug yaratish
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-').replace('--', '-')
        
        # Ikon va rangni avtomatik tanlash
        if not self.icon:
            self.icon = self.get_default_icon()
        if not self.color:
            self.color = self.get_default_color()
        
        super().save(*args, **kwargs)
    
    def get_default_icon(self):
        """Kategoriya turiga qarab default ikon"""
        icons = {
            'food': 'ri-restaurant-line',
            'drink': 'ri-cup-line',
            'clothing': 'ri-t-shirt-line',
            'electronics': 'ri-smartphone-line',
            'furniture': 'ri-sofa-line',
            'book': 'ri-book-line',
            'medicine': 'ri-medicine-bottle-line',
            'tool': 'ri-tools-line',
            'beauty': 'ri-heart-line',
            'sport': 'ri-basketball-line',
        }
        
        name_lower = self.name.lower()
        for key, icon in icons.items():
            if key in name_lower:
                return icon
        return 'ri-folder-line'
    
    def get_default_color(self):
        """Kategoriya turiga qarab default rang"""
        colors = {
            'food': '#10B981',      # Green
            'drink': '#3B82F6',     # Blue
            'clothing': '#8B5CF6',  # Purple
            'electronics': '#F59E0B', # Amber
            'furniture': '#F97316',  # Orange
            'book': '#EC4899',      # Pink
            'medicine': '#EF4444',  # Red
            'tool': '#6B7280',      # Gray
            'beauty': '#8B5CF6',    # Purple
            'sport': '#10B981',     # Green
        }
        
        name_lower = self.name.lower()
        for key, color in colors.items():
            if key in name_lower:
                return color
        return '#3B82F6'
    
    def update_statistics(self):
        """Kategoriya statistikasini yangilash"""
        products = self.products.all()
        self.product_count = products.count()
        self.total_value = sum(p.total_value for p in products if p.total_value)
        self.save()
    
    @property
    def has_subcategories(self):
        """Subkategoriyalari bormi?"""
        return self.subcategories.exists()
    
    @property
    def has_products(self):
        """Mahsulotlari bormi?"""
        return self.products.exists()
    
    def get_full_path(self):
        """Kategoriya to'liq yo'li"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return " → ".join(path)


class Customer(models.Model):
    """Mijozlar modeli"""
    GENDER_CHOICES = [
        ('male', 'Erkak'),
        ('female', 'Ayol'),
        ('other', 'Boshqa'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100, verbose_name="Ism")
    last_name = models.CharField(max_length=100, verbose_name="Familiya")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Telefon")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(blank=True, null=True, verbose_name="Manzil")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Tug'ilgan sana")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name="Jins")
    
    # Additional info
    company = models.CharField(max_length=200, blank=True, null=True, verbose_name="Kompaniya")
    tax_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="STIR")
    notes = models.TextField(blank=True, null=True, verbose_name="Qo'shimcha ma'lumotlar")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    customer_type = models.CharField(max_length=20, choices=[
        ('regular', 'Oddiy'),
        ('wholesale', 'Ulgurji'),
        ('vip', 'VIP'),
        ('employee', 'Xodim'),
    ], default='regular', verbose_name="Mijoz turi")
    
    # Statistics
    total_purchases = models.IntegerField(default=0, verbose_name="Jami xaridlar")
    total_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Jami sarflangan")
    last_purchase = models.DateTimeField(blank=True, null=True, verbose_name="Oxirgi xarid")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Foreign key
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customers")

    class Meta:
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['customer_type']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"
    
    @property
    def full_name(self):
        """To'liq ism-familiya"""
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        # Telefon raqamini formatlash
        if self.phone:
            # Faqat raqamlarni saqlash
            self.phone = ''.join(filter(str.isdigit, self.phone))
        super().save(*args, **kwargs)
    
    def update_statistics(self):
        """Mijoz statistikasini yangilash"""
        from .models import Sale, Debt
        sales = Sale.objects.filter(customer=self)
        debts = Debt.objects.filter(customer=self, status__in=['pending', 'partially_paid'])
        
        self.total_purchases = sales.count()
        self.total_spent = sales.aggregate(total=Sum('total'))['total'] or 0
        self.last_purchase = sales.order_by('-sale_date').first().sale_date if sales.exists() else None
        
        # Qarzni hisoblash
        total_debt = debts.aggregate(
            total=Sum(F('amount') - F('paid_amount'))
        )['total'] or 0
        
        self.save()
        return total_debt
    
    @property
    def total_debt(self):
        """Jami qarzi"""
        from .models import Debt
        debts = Debt.objects.filter(customer=self, status__in=['pending', 'partially_paid'])
        return debts.aggregate(total=Sum(F('amount') - F('paid_amount')))['total'] or 0
    
    @property
    def debt_count(self):
        """Qarzlar soni"""
        from .models import Debt
        return Debt.objects.filter(customer=self, status__in=['pending', 'partially_paid']).count()
    
    def get_loyalty_level(self):
        """Sodiqlik darajasi"""
        if self.total_spent > 10000000:  # 10 million
            return 'diamond'
        elif self.total_spent > 5000000:  # 5 million
            return 'gold'
        elif self.total_spent > 1000000:  # 1 million
            return 'silver'
        elif self.total_spent > 500000:   # 500 ming
            return 'bronze'
        return 'new'


class Product(models.Model):
    """Mahsulot modeli"""
    UNIT_CHOICES = [
        ('kg', 'Kilogram (kg)'),
        ('g', 'Gram (g)'),
        ('pc', 'Dona (pc)'),
        ('l', 'Litr (l)'),
        ('ml', 'Millilitr (ml)'),
        ('pack', 'Paket (pack)'),
        ('box', 'Quti (box)'),
        ('bottle', 'Shisha (bottle)'),
        ('m', 'Metr (m)'),
        ('cm', 'Santimetr (cm)'),
        ('pair', 'Juft (pair)'),
        ('set', 'Komplekt (set)'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Faol'),
        ('inactive', 'Nofaol'),
        ('low_stock', 'Kam qolgan'),
        ('out_of_stock', 'Tugagan'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    name = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU kodi")
    barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name="Shtrix kod")
    
    # Category and classification
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name="products", verbose_name="Kategoriya")
    brand = models.CharField(max_length=100, blank=True, null=True, verbose_name="Brend")
    
    # Pricing
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Kirim narxi")
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sotuv narxi")
    
    # Stock
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="Miqdor")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pc', verbose_name="O'lchov birligi")
    min_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=5, verbose_name="Minimal miqdor")
    
    # Images
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Rasm")
    
    # Description
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Holati")
    
    # Statistics
    total_sold = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="Jami sotilgan")
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Jami daromad")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Foreign key
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def save(self, *args, **kwargs):
        # Statusni yangilash
        self.update_status()
        
        # Agar SKU berilmagan bo'lsa, avtomatik generatsiya qilish
        if not self.sku:
            self.sku = self.generate_sku()
        
        # O'zgarishlarni saqlash
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Kategoriya statistikasini yangilash
        if self.category:
            self.category.update_statistics()
    
    def generate_sku(self):
        """Avtomatik SKU generatsiyasi"""
        prefix = ''.join([word[0].upper() for word in self.name.split()[:3]])
        return f"{prefix}{Product.objects.count() + 1:04d}"
    
    def update_status(self):
        """Mahsulot holatini yangilash"""
        if self.quantity <= 0:
            self.status = 'out_of_stock'
        elif self.quantity <= self.min_quantity:
            self.status = 'low_stock'
        elif self.quantity > self.min_quantity:
            self.status = 'active'
    
    @property
    def profit(self):
        """Foyda"""
        return self.sale_price - self.purchase_price
    
    @property
    def profit_percentage(self):
        """Foyda foizi"""
        if self.purchase_price > 0:
            return (self.profit / self.purchase_price) * 100
        return 0
    
    @property
    def total_value(self):
        """Jami qiymati"""
        return self.quantity * self.purchase_price
    
    @property
    def is_low_stock(self):
        """Minimal chegara yaqinligi"""
        return self.quantity <= self.min_quantity
    
    def get_stock_status_color(self):
        """Zapas holati uchun rang"""
        if self.status == 'out_of_stock':
            return 'red'
        elif self.status == 'low_stock':
            return 'orange'
        return 'green'
    
    def clean(self):
        """Ma'lumotlarni tekshirish"""
        if self.sale_price < self.purchase_price:
            raise ValidationError("Sotuv narxi kirim narxidan past bo'lishi mumkin emas!")
        if self.quantity < 0:
            raise ValidationError("Miqdor manfiy bo'lishi mumkin emas!")


class Sale(models.Model):
    """Sotuvlar modeli"""
    PAYMENT_METHODS = [
        ('cash', 'Naqd pul'),
        ('card', 'Bank kartasi'),
        ('transfer', 'Bank o\'tkazmasi'),
        ('credit', 'Nasiya'),
        ('mixed', 'Aralash'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name="sales", verbose_name="Mijoz")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales", verbose_name="Mahsulot")
    
    # Sale details
    quantity = models.DecimalField(max_digits=12, decimal_places=3, verbose_name="Miqdor")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Narx")
    total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Jami summa")
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash', verbose_name="To'lov usuli")
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="To'langan summa")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Chegirma")
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Soliq")
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Kutilmoqda'),
        ('completed', 'Yakunlangan'),
        ('cancelled', 'Bekor qilingan'),
        ('refunded', 'Qaytarilgan'),
    ], default='completed', verbose_name="Holati")
    
    # Additional info
    invoice_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Faktura raqami")
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    
    # Timestamps
    sale_date = models.DateTimeField(auto_now_add=True, verbose_name="Sotuv sanasi")
    updated_at = models.DateTimeField(auto_now=True)
    
    # Foreign keys
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales")

    class Meta:
        verbose_name = "Sotuv"
        verbose_name_plural = "Sotuvlar"
        ordering = ['-sale_date']
        indexes = [
            models.Index(fields=['sale_date']),
            models.Index(fields=['customer']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Sotuv #{self.invoice_number or self.id}" if self.invoice_number else f"Sotuv {self.id}"
    
    def save(self, *args, **kwargs):
        # Jami summani hisoblash
        self.total = (self.quantity * self.price) - self.discount + self.tax
        
        # Faktura raqamini generatsiya qilish
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        super().save(*args, **kwargs)
        
        # Mahsulot miqdorini yangilash
        self.product.quantity -= self.quantity
        self.product.total_sold += self.quantity
        self.product.total_revenue += self.total
        self.product.save()
        
        # Mijoz statistikasini yangilash
        if self.customer:
            self.customer.update_statistics()
    
    def generate_invoice_number(self):
        """Avtomatik faktura raqami"""
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        count = Sale.objects.filter(sale_date__date=datetime.now().date()).count() + 1
        return f"INV-{date_str}-{count:04d}"
    
    @property
    def profit(self):
        """Sotuvdan foyda"""
        return (self.price - self.product.purchase_price) * self.quantity
    
    @property
    def is_paid(self):
        """To'langanmi?"""
        return self.paid_amount >= self.total
    
    @property
    def remaining_amount(self):
        """Qolgan summa"""
        return self.total - self.paid_amount


class Purchase(models.Model):
    """Kirimlar modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="purchases", verbose_name="Mahsulot")
    supplier = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name="supplies", verbose_name="Yetkazib beruvchi")
    
    # Purchase details
    quantity = models.DecimalField(max_digits=12, decimal_places=3, verbose_name="Miqdor")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Narx")
    total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Jami summa")
    
    # Additional info
    invoice_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Faktura raqami")
    delivery_date = models.DateField(blank=True, null=True, verbose_name="Yetkazib berish sanasi")
    expiry_date = models.DateField(blank=True, null=True, verbose_name="Yaroqlilik muddati")
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Kutilmoqda'),
        ('received', 'Qabul qilingan'),
        ('cancelled', 'Bekor qilingan'),
    ], default='received', verbose_name="Holati")
    
    # Notes
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    
    # Timestamps
    purchase_date = models.DateTimeField(auto_now_add=True, verbose_name="Kirim sanasi")
    updated_at = models.DateTimeField(auto_now=True)
    
    # Foreign key
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases")

    class Meta:
        verbose_name = "Kirim"
        verbose_name_plural = "Kirimlar"
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['purchase_date']),
            models.Index(fields=['supplier']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Kirim #{self.invoice_number}" if self.invoice_number else f"Kirim {self.id}"
    
    def save(self, *args, **kwargs):
        # Jami summani hisoblash
        self.total = self.quantity * self.price
        
        # Mahsulot miqdorini yangilash
        if self.status == 'received':
            self.product.quantity += self.quantity
            self.product.save()
        
        super().save(*args, **kwargs)
    
    @property
    def unit_price(self):
        """Birlik narxi"""
        return self.price / self.quantity if self.quantity else 0


class Debt(models.Model):
    """Qarzlar modeli"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="debts", verbose_name="Mijoz")
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="debts", verbose_name="Sotuv")
    
    # Debt details
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Jami summa")
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="To'langan summa")
    
    # Dates
    due_date = models.DateField(verbose_name="Muddat")
    paid_date = models.DateField(blank=True, null=True, verbose_name="To'langan sana")
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Kutilmoqda'),
        ('partially_paid', 'Qisman to\'langan'),
        ('paid', 'To\'langan'),
        ('overdue', 'Muddati otgan'),
        ('cancelled', 'Bekor qilingan'),
    ], default='pending', verbose_name="Holati")
    
    # Additional info
    notes = models.TextField(blank=True, null=True, verbose_name="Izohlar")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Foreign key
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="debts")

    class Meta:
        verbose_name = "Qarz"
        verbose_name_plural = "Qarzlar"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"Qarz: {self.customer.full_name} - {self.remaining_amount}"
    
    def save(self, *args, **kwargs):
        # Statusni yangilash
        self.update_status()
        super().save(*args, **kwargs)
        
        # Mijoz statistikasini yangilash
        self.customer.update_statistics()
    
    def update_status(self):
        """Qarz holatini yangilash"""
        from datetime import date
        
        if self.paid_amount >= self.amount:
            self.status = 'paid'
            self.paid_date = date.today()
        elif self.paid_amount > 0:
            self.status = 'partially_paid'
        elif date.today() > self.due_date:
            self.status = 'overdue'
        else:
            self.status = 'pending'
    
    @property
    def remaining_amount(self):
        """Qolgan summa"""
        return self.amount - self.paid_amount
    
    @property
    def is_overdue(self):
        """Muddati o'tganmi?"""
        from datetime import date
        return date.today() > self.due_date and self.status != 'paid'
    
    @property
    def days_overdue(self):
        """Necha kun kechikkan"""
        from datetime import date
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0


class DashboardStats(models.Model):
    """Dashboard statistikasi"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Daily statistics
    date = models.DateField(unique=True, verbose_name="Sana")
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Jami sotuvlar")
    total_purchases = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Jami kirimlar")
    total_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Jami foyda")
    total_customers = models.IntegerField(default=0, verbose_name="Jami mijozlar")
    total_products = models.IntegerField(default=0, verbose_name="Jami mahsulotlar")
    total_debt = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Jami qarz")
    
    # Additional stats
    sales_count = models.IntegerField(default=0, verbose_name="Sotuvlar soni")
    purchase_count = models.IntegerField(default=0, verbose_name="Kirimlar soni")
    new_customers = models.IntegerField(default=0, verbose_name="Yangi mijozlar")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dashboard statistikasi"
        verbose_name_plural = "Dashboard statistikasi"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"Statistika: {self.date}"
    
    @classmethod
    def update_todays_stats(cls):
        """Bugungi statistikani yangilash"""
        from datetime import date
        from django.db.models import Sum, Count
        
        today = date.today()
        stats, created = cls.objects.get_or_create(date=today)
        
        # Sotuvlar
        from .models import Sale
        sales_today = Sale.objects.filter(sale_date__date=today, status='completed')
        stats.total_sales = sales_today.aggregate(total=Sum('total'))['total'] or 0
        stats.sales_count = sales_today.count()
        
        # Kirimlar
        from .models import Purchase
        purchases_today = Purchase.objects.filter(purchase_date__date=today, status='received')
        stats.total_purchases = purchases_today.aggregate(total=Sum('total'))['total'] or 0
        stats.purchase_count = purchases_today.count()
        
        # Foyda
        total_profit = 0
        for sale in sales_today:
            total_profit += sale.profit
        stats.total_profit = total_profit
        
        # Mijozlar
        from .models import Customer
        stats.total_customers = Customer.objects.filter(is_active=True).count()
        stats.new_customers = Customer.objects.filter(created_at__date=today).count()
        
        # Mahsulotlar
        from .models import Product
        stats.total_products = Product.objects.count()
        
        # Qarzlar
        from .models import Debt
        stats.total_debt = Debt.objects.filter(status__in=['pending', 'partially_paid', 'overdue']).aggregate(
            total=Sum('remaining_amount')
        )['total'] or 0
        
        stats.save()
        return stats



class CategoryHistory(models.Model):
    """Kategoriya tarixi"""
    ACTION_CHOICES = [
        ('created', 'Yaratildi'),
        ('updated', 'Yangilandi'),
        ('deleted', 'Oʻchirildi'),
        ('product_added', 'Mahsulot qoʻshildi'),
        ('product_removed', 'Mahsulot olib tashlandi'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="history")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.category.name} - {self.action}"