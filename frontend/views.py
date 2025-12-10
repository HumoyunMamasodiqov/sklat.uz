from django.shortcuts import render


def base(request):
    return render(request, 'base.html')


def home(request):
    return render(request, 'home.html')
def mahsulotlar(request):
    return render(request, 'mahsulotlar.html')
def analitika(request):
    return render(request, 'analitika.html')
def mijozlar(request):
    return render(request, 'mijozlar.html')
def sozlamalar(request):
    return render(request, 'sozlamalar.html')