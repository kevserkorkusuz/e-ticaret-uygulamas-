from django.contrib import admin
from .models import *

class SepetAdmin(admin.ModelAdmin):
    list_display = ['user', 'urun', 'adet', 'toplamFiyat', 'odendiMi']
    list_filter = ['odendiMi']
    ordering = ['-created_at']

class OdemeAdmin(admin.ModelAdmin):
    list_display= ['buyer', 'toplam', 'odendiMi']

# Register your models here.
admin.site.register(Urun)
admin.site.register(Kategori)
admin.site.register(AltKategori)
admin.site.register(Tek)
admin.site.register(Sepet, SepetAdmin)
admin.site.register(Odeme, OdemeAdmin)
