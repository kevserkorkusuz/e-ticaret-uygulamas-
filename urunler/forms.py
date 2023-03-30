from django.forms import ModelForm
from .models import *

class UrunForm (ModelForm):
    class Meta:
        model=Urun
        fields= ['isim', 'kategori', 'altkategori', 'aciklama', 'fiyat', 'resim' ]

    def __init__(self, *args, **kwars):
        super(UrunForm, self).__init__(*args, **kwars)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})