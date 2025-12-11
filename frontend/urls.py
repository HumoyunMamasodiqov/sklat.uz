from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.base, name='base'),
    path('home/', views.home, name='home'),
    path('mahsulotlar/', views.mahsulotlar, name='mahsulotlar'),
    path('analitika/', views.analitika, name='analitika'),
    path('mijozlar/', views.mijozlar, name='mijozlar'),
    path('sozlamalar/', views.sozlamalar, name='sozlamalar'),
]  

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
