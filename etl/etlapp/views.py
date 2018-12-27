from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from openpyxl import Workbook

from .models import Products

from static.etlapp.ScrapperRedux1 import get_tire_widths

def index(request):
    products_list = Products.objects.order_by('-pub_date')
    widths_list = get_tire_widths()
    template = loader.get_template('etlapp/index.html')
    context = {
        'products_list': products_list,
        'widths_list': widths_list,
    }
    # return HttpResponse(template.render(context, request))
    return render(request, 'etlapp/index.html', context)

def save_file(request):
    if request.method == "POST":
        data = {}
        generate_csv(Products.objects.all(), 'static/etlapp/files_from_database/oponeo.csv')
        # for product in Products.objects.all():
        #     print(product.Name)
        return JsonResponse(data)

    return render(request, 'etlapp/index.html')

def generate_csv(Products, file_path):
    wb = Workbook()
    ws = wb.active
    row_count = 1

    ws['A' + str(row_count)] = "ID BD"
    ws['B' + str(row_count)] = "ID Oponeo"
    ws['C' + str(row_count)] = "Producent"
    ws['D' + str(row_count)] = "Nazwa"
    ws['E' + str(row_count)] = "Cena"
    ws['F' + str(row_count)] = "Typ pojazdu"
    ws['G' + str(row_count)] = "Sezon"
    ws['H' + str(row_count)] = "Szerokość"
    ws['I' + str(row_count)] = "Rozmiar"
    ws['J' + str(row_count)] = "Homologacja"
    ws['K' + str(row_count)] = "Indeks prędkości"
    ws['L' + str(row_count)] = "Indeks nośności"
    ws['M' + str(row_count)] = "Etykieta UE"
    ws['N' + str(row_count)] = "Rok produkcji"
    ws['O' + str(row_count)] = "Kraj produkcji"
    ws['P' + str(row_count)] = "Gwarancja"
    ws['Q' + str(row_count)] = "Inne"
    ws['R' + str(row_count)] = "Data publikacji w bazie"
    row_count += 1

    for product in Products:
        ws['A' + str(row_count)] = product.id
        ws['B' + str(row_count)] = product.ProductID
        ws['C' + str(row_count)] = product.Manufacturer
        ws['D' + str(row_count)] = product.Name
        ws['E' + str(row_count)] = product.Price
        ws['F' + str(row_count)] = product.Car_type
        ws['G' + str(row_count)] = product.season
        ws['H' + str(row_count)] = product.tire_width
        ws['I' + str(row_count)] = product.size
        ws['J' + str(row_count)] = product.approval
        ws['K' + str(row_count)] = product.speed_index
        ws['L' + str(row_count)] = product.weight_index
        ws['M' + str(row_count)] = product.sound_index
        ws['N' + str(row_count)] = product.production_year
        ws['O' + str(row_count)] = product.country_of_origin
        ws['P' + str(row_count)] = product.guaranty
        ws['Q' + str(row_count)] = product.other_info
        ws['R' + str(row_count)] = product.pub_date
        row_count += 1

    wb.save(file_path)
