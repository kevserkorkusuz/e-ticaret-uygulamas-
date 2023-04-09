from django.shortcuts import render, redirect
from .models import *
from django.db.models import Q
from django.contrib import messages
from .forms import *
import iyzipay
import json
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
from django.contrib import messages
import pprint
from django.core.cache import cache

#iyzico ssl sorunu çıkardığı için yazdığım kod

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

#buraya kadar sertifika kontrolünü devre dışı bır

# Create your views here.
api_key = 'sandbox-rcd7070oMFm2sedKcqTsCNSzldKzQgrp'
secret_key = 'sandbox-lO7b5wf1Q6PNGYYc2pROtrnxasi9jdqV'
base_url = 'sandbox-api.iyzipay.com'


options = {
    'api_key': api_key,
    'secret_key': secret_key,
    'base_url': base_url
}
sozlukToken = list()


def payment(request):
    context = dict()
    odeme= Odeme.objects.get(buyer= request.user, odendiMi =False)

    buyer={
        'id': odeme.buyer.id,
        'name': request.user.username,
        'surname': 'Doe',
        'gsmNumber': '+905350000000',
        'email': request.user.email,
        'identityNumber': '74300864791',
        'lastLoginDate': '2015-10-05 12:43:35',
        'registrationDate': '2013-04-21 15:12:09',
        'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'ip': '85.34.78.112',
        'city': 'Istanbul',
        'country': 'Turkey',
        'zipCode': '34732'
    }

    address={
        'contactName': 'Jane Doe',
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
        'zipCode': '34732'
    }

    basket_items=[
        {
            'id': 'BI101',
            'name': 'Binocular',
            'category1': 'Collectibles',
            'category2': 'Accessories',
            'itemType': 'PHYSICAL',
            'price': '0.3'
        },
        {
            'id': 'BI102',
            'name': 'Game code',
            'category1': 'Game',
            'category2': 'Online Game Items',
            'itemType': 'VIRTUAL',
            'price': '0.5'
        },
        {
            'id': 'BI103',
            'name': 'Usb',
            'category1': 'Electronics',
            'category2': 'Usb / Cable',
            'itemType': 'PHYSICAL',
            'price': '0.2'
        }
    ]

    request={
        'locale': 'tr',
        'conversationId': '123456789',
        'price': '1',
        'paidPrice': odeme.toplam,
        'currency': 'TRY',
        'basketId': 'B67832',
        'paymentGroup': 'PRODUCT',
        "callbackUrl": "http://127.0.0.1:8000/result/",
        "enabledInstallments": ['2', '3', '6', '9'],
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items,
        # 'debitCardAllowed': True
    }

    checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request, options)

    #print(checkout_form_initialize.read().decode('utf-8'))
    page = checkout_form_initialize
    header = {'Content-Type': 'application/json'}
    content = checkout_form_initialize.read().decode('utf-8')
    json_content = json.loads(content)
    print(type(json_content))
    print(json_content["checkoutFormContent"])
    print("************************")
    print(json_content["token"])
    print("************************")
    token =json_content['token']
    cache.set('token', token)   
    sozlukToken.append(json_content["token"])
    return HttpResponse(f'<div id="iyzipay-checkout-form" class="responsive"> {json_content["checkoutFormContent"]} </div>')
    


@require_http_methods(['POST'])
@csrf_exempt
def result(request):
    context = dict()

    url = request.META.get('index')
    token = cache.get('token')

    request = {
        'locale': 'tr',
        'conversationId': '123456789',
        'token': token
    }
    checkout_form_result = iyzipay.CheckoutForm().retrieve(request, options)
    print("************************")
    print(type(checkout_form_result))
    result = checkout_form_result.read().decode('utf-8')
    print("************************")
    print(sozlukToken[0])   # Form oluşturulduğunda 
    print("************************")
    print("************************")
    sonuc = json.loads(result, object_pairs_hook=list)
    #print(sonuc[0][1])  # İşlem sonuç Durumu dönüyor
    #print(sonuc[5][1])   # Test ödeme tutarı
    print("************************")
    for i in sonuc:
        print(i)
    print("************************")
    print(sozlukToken)
    print("************************")
    if sonuc[0][1] == 'success':
        context['success'] = 'Başarılı İŞLEMLER'
        return HttpResponseRedirect(reverse('success'), context)

    elif sonuc[0][1] == 'failure':
        context['failure'] = 'Başarısız'
        return HttpResponseRedirect(reverse('failure'), context)

    return HttpResponse(url)



def success(request):
    sepet = Sepet.objects.filter(user = request.user, odendiMi =False)
    for i in sepet:
        i.odendiMi=True
        i.save()
    odeme = Odeme.objects.get(buyer=request.user, odendiMi =False)
    odeme.odendiMi =True
    odeme.save()
    messages.success(request, 'Ödeme Başarılı')
    return redirect('index')


def fail(request):
    context = dict()
    context['fail'] = 'İşlem Başarısız'

    template = 'fail.html'
    return render(request, template, context)

def index(request):
    urunler = Urun.objects.all()
    kategoriler =Kategori.objects.all()
    search=''
    if request.GET.get('search'):
        search= request.GET.get('search')
        urunler = Urun.objects.filter(
            Q(isim__icontains = search ) |
            Q(aciklama__icontains = search ) |
            Q(kategori__isim__icontains = search)
        )
    if request.method == 'POST':
        if request.user.is_authenticated:
            urunId= request.POST['urunId']
            adet= request.POST['adet']
            urun = Urun.objects.get(id=urunId)
            if Sepet.objects.filter(user=request.user, urun=urun, odendiMi=False).exists():
                sepet = Sepet.objects.get(user=request.user, urun=urun, odendiMi=False)
                sepet.adet +=int(adet)
                sepet.toplamFiyat= sepet.urun.fiyat * sepet.adet
                sepet.save()
                messages.success(request, 'Sepete eklendi.')
                return redirect('index')
            else:
                sepet= Sepet.objects.create(
                    user= request.user,
                    urun=urun,
                    adet=adet,
                    toplamFiyat = urun.fiyat *int(adet)
                )
                sepet.save()
                messages.success(request, 'Sepete Eklendi.')
                return redirect('index')
        else:
            messages.warning(request,  "Lütfen giriş yapınız.")
            return redirect ('login')
    context= {
        'product': urunler,
        'search': search,
        'kategoriler':kategoriler
    }
    
    return render(request, 'index.html',context)

def urun(request,urunId):
    urun = Urun.objects.get(id = urunId)
    context = {
        'urun':urun
    }
    return render(request, 'urun.html',context)

def olustur(request):
    form = UrunForm()
    if request.method == 'POST':
        form =UrunForm(request.POST, request.FILES)
        if form.is_valid():
            yeniUrun=form.save(commit=False)
            yeniUrun.satici=request.user
            yeniUrun.save()
            messages.success(request, 'Ürün oluşturuldu')
            return redirect('index')
        

    context= {
        'form':form
    }
    return render(request, 'olustur.html', context)

def sepet(request):
    sepet= Sepet.objects.filter(user = request.user, odendiMi= False)
    toplam = 0
    for i in sepet:
        toplam +=i.toplamFiyat
    if request.method == 'POST':
        if 'sil' in request.POST:
            sepetId= request.POST['urunId']
            sepet = Sepet.objects.get(id=sepetId)
            sepet.delete()
            return redirect ('sepet')
        else:
            if Odeme.objects.filter(buyer=request.user, odendiMi= False).exists():
                return redirect('payment')
            else:
                odeme = Odeme.objects.create(
                    buyer= request.user,
                    toplam=toplam,
                )
                odeme.sepet.add(*sepet)
                odeme.save()
                return redirect('payment')
    context = {
        'sepet':sepet,
        'toplam':toplam
    }
    return render(request, 'sepet.html', context)