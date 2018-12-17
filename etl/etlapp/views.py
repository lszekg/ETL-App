from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Products

#from static.etlapp.ScrapperRedux1 import get_tire_widths

def index(request):
    products_list = Products.objects.order_by('-pub_date')
    #widths_list = get_tire_widths()
    template = loader.get_template('etlapp/index.html')
    context = {
        'products_list': products_list,
        #'widths_list': widths_list,
    }
    return HttpResponse(template.render(context, request))
