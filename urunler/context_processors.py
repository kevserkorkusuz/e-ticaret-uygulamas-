from .models import *

def get_len_sepets (request):
    if request.user.is_authenticated:
        uzun = Sepet.objects.filter(user=request.user, odendiMi =False).count()
    else:
        uzun=0
    return {'uzun':uzun}

def get_categories(request):
    kategoriler =Kategori.objects.all()
    return {'kategoriler': kategoriler} 